from dataclasses import dataclass

from app.domain.models import Tokens
from app.domain.ports import (
    AuthCommandPort,
    AuthQueryPort,
    TokenServicePort,
)


@dataclass
class TokenRefreshUseCase:
    db_cmd: AuthCommandPort
    db_query: AuthQueryPort
    token_service: TokenServicePort


async def refresh_token(
    plain_refresh_token: str,
    use_case: TokenRefreshUseCase,
) -> Tokens:
    """Exchange an old token for a new one.

    Raises:
        UnauthorizedError: if old token not in database
        UnavailableError: if any service is down

    """
    # compare request token with token in database
    user_id = await use_case.db_query.get_token_owner(plain_token=plain_refresh_token)

    # generate authentication tokens
    tokens = use_case.token_service.generate_token_pair(user_id=user_id)

    # save data in database (hashing take place within the adapters)
    await use_case.db_cmd.update_session(
        user_id=user_id,
        plain_refresh_token=tokens.refresh_token,
    )

    return tokens
