import uuid
from unittest.mock import patch

import pytest

from app.domain.models import RefreshToken, Tokens
from app.domain.ports import (
    DatabaseCommandPort,
    DatabaseQueryPort,
    JWTPort,
)
from app.use_cases.refresh_token import (
    TokenRefreshService,
    handle_refresh_token_event,
)


@pytest.fixture
def services(
    mock_db_cmd: DatabaseCommandPort,
    mock_db_queries: DatabaseQueryPort,
    mock_jwt_port: JWTPort,
) -> TokenRefreshService:
    return TokenRefreshService(
        db_cmd=mock_db_cmd,
        db_queries=mock_db_queries,
        jwt_port=mock_jwt_port,
    )


async def test_handle_refresh_token(
    services: TokenRefreshService,
) -> None:
    test_token = "test_refresh_token"
    request = RefreshToken(token=test_token)
    fixed_refresh_token = uuid.uuid4()
    with patch(
        "app.domain.events.token_refreshed.uuid4",
        return_value=fixed_refresh_token,
    ):
        result = await handle_refresh_token_event(request, services)

    assert isinstance(result, Tokens)

    expected_user_id = services.db_queries.get_user_id_by_token.return_value

    services.db_queries.get_user_id_by_token.assert_called_once_with(request.token)
    services.jwt_port.create_token.assert_called_once_with(expected_user_id)

    services.db_cmd.refresh_session.assert_called_once_with(
        expected_user_id,
        fixed_refresh_token,
    )
