from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.errors import UnauthorizedError
from app.domain.models import ProzUser, Tokens
from app.domain.ports import (
    ProzClientPort,
)
from app.domain.use_cases.exchange_token import CodeExchangeUseCase, exchange_token


@pytest.fixture
def mock_proz_client(
    test_user: ProzUser,
    test_tokens: Tokens,
) -> AsyncMock:
    test_proz_client = AsyncMock(spec=ProzClientPort)
    test_proz_client.exchange_code_for_tokens = AsyncMock(return_value=test_tokens)
    test_proz_client.get_token_owner = AsyncMock(return_value=test_user)
    return test_proz_client


@pytest.fixture
def mock_exchange_token_use_case(
    mock_auth_cmd: AsyncMock,
    mock_auth_query: AsyncMock,
    mock_proz_client: AsyncMock,
    mock_token_service: MagicMock,
    mock_clock: MagicMock,
) -> CodeExchangeUseCase:
    return CodeExchangeUseCase(
        db_cmd=mock_auth_cmd,
        db_query=mock_auth_query,
        proz_client=mock_proz_client,
        token_service=mock_token_service,
        clock=mock_clock,
    )


async def test_exchange_token(
    mock_exchange_token_use_case: CodeExchangeUseCase,
) -> None:
    use_case = mock_exchange_token_use_case
    test_code = "2eb10703-72eb-4e38-b7ed-2f7f811973a0"

    result = await exchange_token(test_code, use_case)
    assert result == use_case.token_service.generate_token_pair.return_value

    # fetch info about proz user
    use_case.proz_client.exchange_code_for_tokens.assert_awaited_once_with(
        code=test_code,
    )
    use_case.proz_client.get_token_owner.assert_awaited_once_with(
        access_token=use_case.proz_client.exchange_code_for_tokens.return_value.access_token,
    )

    # check membership
    use_case.clock.now.assert_called_once()
    use_case.proz_client.get_token_owner.return_value.membership.ensure_active.assert_called_once_with(
        today=use_case.clock.now.return_value,
    )

    # generate authentication tokens
    use_case.token_service.generate_token_pair.assert_called_once_with(
        user_id=use_case.proz_client.get_token_owner.return_value.id,
    )

    # upsert to database
    use_case.db_cmd.upsert_proz_info.assert_called_once_with(
        proz_user=use_case.proz_client.get_token_owner.return_value,
        plain_proz_refresh_token=use_case.proz_client.exchange_code_for_tokens.return_value.refresh_token,
        plain_refresh_token=use_case.token_service.generate_token_pair.return_value.refresh_token,
    )


async def test_exchange_token_invalid_membership(
    mock_exchange_token_use_case: CodeExchangeUseCase,
) -> None:
    use_case = mock_exchange_token_use_case
    test_code = "2eb10703-72eb-4e38-b7ed-2f7f811973a0"
    use_case.proz_client.get_token_owner.return_value.membership.ensure_active.side_effect = (  # ruff:ignore[line-too-long]
        UnauthorizedError()
    )

    with pytest.raises(UnauthorizedError):
        await exchange_token(test_code, use_case)

    use_case.token_service.generate_token_pair.assert_not_called()
    use_case.db_cmd.upsert_proz_info.assert_not_awaited()
