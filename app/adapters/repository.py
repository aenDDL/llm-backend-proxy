from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from uuid import UUID

from asyncpg import Pool

from app.adapters.security_service import Encrypter, Hasher
from app.domain.errors import UnauthorizedError
from app.domain.models import ChatDetails, ProzUser


class SQLQuery(StrEnum):
    INSERT_CHAT_DETAILS = "insert_chat_details.sql"
    SELECT_TOKEN_OWNER = "select_token_owner.sql"
    SELECT_USER_ID = "select_user_id.sql"
    UPDATE_SESSION = "update_session.sql"
    UPSERT_PROZ_USER = "upsert_proz_user.sql"
    UPSERT_APP_TOKEN = "upsert_app_token.sql"


@dataclass(frozen=True)
class SQLQueries:
    queries: dict[SQLQuery, str]

    def __getitem__(self, query: SQLQuery) -> str:
        return self.queries[query]


def load_all_sql(sql_dir: Path) -> SQLQueries:
    queries = {
        member: (sql_dir / member.value).read_text(encoding="utf-8")
        for member in SQLQuery
    }
    return SQLQueries(queries)


@dataclass
class AuthCommand:
    pool: Pool
    hasher: Hasher
    encrypter: Encrypter
    sql_reader: SQLQueries

    async def upsert_proz_info(
        self,
        proz_user: ProzUser,
        plain_proz_refresh_token: str,
        plain_refresh_token: str,
    ) -> None:
        hashed_refresh_token = self.hasher.hash(plain_refresh_token)
        encrypted_proz_refresh_token = self.encrypter.encrypt(plain_proz_refresh_token)

        async with self.pool.acquire() as conn, conn.transaction():
            await conn.execute(
                self.sql_reader[SQLQuery.UPSERT_PROZ_USER],
                proz_user.id,
                proz_user.name,
                proz_user.membership.type if proz_user.membership else None,
                proz_user.membership.expire_on if proz_user.membership else None,
                encrypted_proz_refresh_token,
            )
            await conn.execute(
                self.sql_reader[SQLQuery.UPSERT_APP_TOKEN],
                proz_user.id,
                hashed_refresh_token,
            )

    async def update_session(self, user_id: UUID, plain_refresh_token: str) -> None:
        hashed_refresh_token = self.hasher.hash(plain_refresh_token)

        async with self.pool.acquire() as conn:
            await conn.execute(
                self.sql_reader[SQLQuery.UPDATE_SESSION],
                hashed_refresh_token,
                str(user_id),
            )


@dataclass
class ChatCommand:
    pool: Pool
    sql_reader: SQLQueries

    async def save_chat_details(self, user_id: UUID, details: ChatDetails) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                self.sql_reader[SQLQuery.INSERT_CHAT_DETAILS],
                user_id,
                details.model,
                details.tokens_total,
                details.cost_usd,
            )


@dataclass
class AuthQuery:
    pool: Pool
    hasher: Hasher
    sql_reader: SQLQueries

    async def check_if_user_exists(self, user_id: UUID) -> None:
        async with self.pool.acquire() as conn:
            existing_user = await conn.fetchval(
                self.sql_reader[SQLQuery.SELECT_USER_ID],
                user_id,
            )
        if not existing_user:
            msg = "User does not exists"
            raise UnauthorizedError(msg)

    async def get_token_owner(self, plain_token: str) -> UUID:
        hashed_token = self.hasher.hash(plain_token)
        async with self.pool.acquire() as conn:
            token_owner = await conn.fetchval(
                self.sql_reader[SQLQuery.SELECT_TOKEN_OWNER],
                hashed_token,
            )
        if not token_owner:
            msg = "Refresh token does not exists"
            raise UnauthorizedError(msg)
        return token_owner
