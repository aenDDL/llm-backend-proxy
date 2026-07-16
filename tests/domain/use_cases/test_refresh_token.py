from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.errors import UnauthorizedError
from app.domain.use_cases.refresh_token import TokenRefreshUseCase, refresh_token


@pytest.fixture
def mock_refresh_token_use_case(
    mock_auth_cmd: AsyncMock,
    mock_auth_query: AsyncMock,
    mock_token_service: MagicMock,
    mock_clock: MagicMock,
) -> TokenRefreshUseCase:
    return TokenRefreshUseCase(
        db_cmd=mock_auth_cmd,
        db_query=mock_auth_query,
        token_service=mock_token_service,
        clock=mock_clock,
    )


async def test_refresh_token(mock_refresh_token_use_case: TokenRefreshUseCase) -> None:
    use_case = mock_refresh_token_use_case
    plain_token = "2eb10703-72eb-4e38-b7ed-2f7f811973a0"

    result = await refresh_token(plain_token, use_case)
    assert result == use_case.token_service.generate_token_pair.return_value

    # compare request token with token in database
    use_case.db_query.get_token_owner.assert_awaited_once_with(
        plain_token=plain_token,
    )

    # check membership
    use_case.clock.now.assert_called_once()
    use_case.db_query.get_proz_status_info.return_value.ensure_active.assert_called_once_with(
        today=use_case.clock.now.return_value,
    )

    # generate authentication tokens
    use_case.token_service.generate_token_pair.assert_called_once_with(
        user_id=use_case.db_query.get_token_owner.return_value,
    )

    # save data in database
    use_case.db_cmd.update_session.assert_awaited_once_with(
        user_id=use_case.db_query.get_token_owner.return_value,
        plain_refresh_token=use_case.token_service.generate_token_pair.return_value.refresh_token,
    )


async def test_refresh_token_invalid_membership(
    mock_refresh_token_use_case: TokenRefreshUseCase,
) -> None:
    use_case = mock_refresh_token_use_case
    plain_token = "2eb10703-72eb-4e38-b7ed-2f7f811973a0"
    use_case.db_query.get_proz_status_info.return_value.ensure_active.side_effect = (
        UnauthorizedError()
    )

    with pytest.raises(UnauthorizedError):
        await refresh_token(plain_token, use_case)

    use_case.token_service.generate_token_pair.assert_not_called()
    use_case.db_cmd.update_session.assert_not_awaited()
