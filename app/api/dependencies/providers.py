from collections.abc import AsyncIterator

import asyncpg
from dishka import Provider, Scope, provide
from httpx import AsyncClient

from app.adapters import (
    AuthCommand,
    AuthQuery,
    ChatCommand,
    Clock,
    Encrypter,
    Hasher,
    ProzClient,
    SQLQueries,
    TokenService,
)
from app.adapters.repository import load_all_sql
from app.domain.ports import (
    AuthCommandPort,
    AuthQueryPort,
    ChatCommandPort,
    ClockPort,
    ProzClientPort,
    TokenServicePort,
)
from app.domain.use_cases import ChatUseCase, CodeExchangeUseCase, TokenRefreshUseCase
from app.infrastructure.config import Settings


def provide_repositories() -> Provider:
    repository_provider = Provider(scope=Scope.REQUEST)
    repository_provider.provide(AuthQuery, provides=AuthQueryPort)
    repository_provider.provide(AuthCommand, provides=AuthCommandPort)
    repository_provider.provide(ChatCommand, provides=ChatCommandPort)

    return repository_provider


def provide_use_cases() -> Provider:
    services_provider = Provider(scope=Scope.REQUEST)
    services_provider.provide(ChatUseCase)
    services_provider.provide(CodeExchangeUseCase)
    services_provider.provide(TokenRefreshUseCase)

    return services_provider


def provide_clock() -> Provider:
    clock_provider = Provider(scope=Scope.APP)
    clock_provider.provide(Clock, provides=ClockPort)
    return clock_provider


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def pool(self, s: Settings) -> AsyncIterator[asyncpg.Pool]:
        pool = await asyncpg.create_pool(
            dsn=s.db_url,
            min_size=s.db.pg_pool_min_size,
            max_size=s.db.pg_pool_max_size,
        )
        yield pool
        await pool.close()

    @provide(scope=Scope.APP)
    async def sql_reader(self, settings: Settings) -> SQLQueries:
        return load_all_sql(settings.sql_path)


class SecurityProvider(Provider):
    @provide(scope=Scope.APP, provides=TokenServicePort)
    def tokens(self, s: Settings) -> TokenService:
        return TokenService(
            secret_key=s.tokens.secret_key,
            algorithm=s.tokens.algorithm,
            access_token_expire_minutes=s.tokens.access_token_expire_minutes,
        )

    @provide(scope=Scope.APP)
    def hasher(self, s: Settings) -> Hasher:
        return Hasher(secret_key=s.cryptography.secret_key_to_hash)

    @provide(scope=Scope.APP)
    def encrypter(self, s: Settings) -> Encrypter:
        return Encrypter(secret_key=s.cryptography.secret_key_to_encrypt)


class HTTPClientProvider(Provider):
    @provide(scope=Scope.APP)
    async def http_client(self, s: Settings) -> AsyncIterator[AsyncClient]:
        async with AsyncClient(timeout=s.network.timeout) as client:
            yield client


class ProzClientProvider(Provider):
    @provide(scope=Scope.APP, provides=ProzClientPort)
    def proz_client(self, s: Settings, http_client: AsyncClient) -> ProzClient:
        return ProzClient(
            http_client=http_client,
            client_id=s.proz.proz_client_id,
            client_secret=s.proz.proz_client_secret,
            redirect_uri=s.proz.proz_redirect_uri,
            user_url=s.proz.user_url,
            token_url=s.proz.token_url,
        )


def provide_deps() -> tuple[Provider]:
    return (
        DatabaseProvider(),
        HTTPClientProvider(),
        ProzClientProvider(),
        SecurityProvider(),
        SettingsProvider(),
        provide_clock(),
    )
