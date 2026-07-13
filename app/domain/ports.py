from collections.abc import AsyncIterator
from datetime import date
from typing import Protocol
from uuid import UUID

from app.domain.models import (
    ChatDetails,
    ChatPrompts,
    ProzMembership,
    ProzUser,
    Tokens,
)


class TokenServicePort(Protocol):
    def generate_token_pair(self, user_id: UUID) -> Tokens: ...
    def verify_token(self, token: str) -> UUID: ...


class ProzClientPort(Protocol):
    async def exchange_code_for_tokens(self, code: str) -> Tokens: ...
    async def get_token_owner(self, access_token: str) -> ProzUser: ...


class AuthCommandPort(Protocol):
    async def upsert_proz_info(
        self,
        proz_user: ProzUser,
        plain_proz_refresh_token: str,
        plain_refresh_token: str,
    ) -> None: ...
    async def update_session(self, user_id: UUID, plain_refresh_token: str) -> None: ...


class ChatCommandPort(Protocol):
    async def save_chat_details(self, user_id: UUID, details: ChatDetails) -> None: ...


class AuthQueryPort(Protocol):
    async def check_if_user_exists(self, user_id: UUID) -> None: ...
    async def get_token_owner(self, plain_token: str) -> UUID: ...
    async def get_proz_status_info(self, user_id: UUID) -> ProzMembership: ...


class ChatServicePort(Protocol):
    def run_stream(self, prompts: ChatPrompts) -> AsyncIterator[str]: ...
    def get_details(self) -> ChatDetails: ...


class ClockPort(Protocol):
    def now(self) -> date: ...
