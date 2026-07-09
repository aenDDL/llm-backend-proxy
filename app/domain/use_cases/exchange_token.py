from dataclasses import dataclass

from app.domain.models import Tokens
from app.domain.ports import (
    AuthCommandPort,
    AuthQueryPort,
    ProzClientPort,
    TokenServicePort,
)


@dataclass
class CodeExchangeUseCase:
    db_cmd: AuthCommandPort
    db_query: AuthQueryPort
    proz_client: ProzClientPort
    token_service: TokenServicePort


async def exchange_token(code: str, use_case: CodeExchangeUseCase) -> Tokens:
    """Authorize user and register in database.

    Raises:
        UnauthorizedError: if ProZ code invalid
        UnavailableError: if any service is down

    """
    # fetch info about proz user
    proz_tokens = await use_case.proz_client.exchange_code_for_tokens(code=code)
    proz_user = await use_case.proz_client.get_token_owner(
        access_token=proz_tokens.access_token,
    )

    # generate authentication tokens
    tokens = use_case.token_service.generate_token_pair(user_id=proz_user.id)

    # upsert to database
    await use_case.db_cmd.upsert_proz_info(
        proz_user=proz_user,
        plain_proz_refresh_token=proz_tokens.refresh_token,
        plain_refresh_token=tokens.refresh_token,
    )

    return tokens
