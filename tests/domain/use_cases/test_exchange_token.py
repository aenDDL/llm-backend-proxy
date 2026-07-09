import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.models import ProzCode, ProzTokens, ProzUser, Tokens
from app.domain.ports import (
    DatabaseCommandPort,
    DatabaseQueryPort,
    JWTPort,
    ProzClientPort,
)
from app.use_cases.exchange_token import (
    TokenCreateService,
    handle_create_token_via_proz_event,
)


@pytest.fixture
def proz_user() -> ProzUser:
    return ProzUser(id=uuid.uuid4(), name="test_name")


@pytest.fixture
def proz_tokens() -> ProzTokens:
    test_access_token = "test"
    test_refresh_token = "test"
    return ProzTokens(
        access_token=test_access_token,
        refresh_token=test_refresh_token,
    )


@pytest.fixture
def mock_proz_client_port(proz_user: ProzUser, proz_tokens: ProzTokens) -> AsyncMock:
    proz_client_service = AsyncMock(spec=ProzClientPort)
    proz_client_service.exchange_code_for_tokens = AsyncMock(return_value=proz_tokens)
    proz_client_service.get_token_owner.return_value = proz_user
    return proz_client_service


@pytest.fixture
def services(
    mock_db_cmd: DatabaseCommandPort,
    mock_db_queries: DatabaseQueryPort,
    mock_proz_client_port: ProzClientPort,
    mock_jwt_port: JWTPort,
) -> TokenCreateService:
    return TokenCreateService(
        db_cmd=mock_db_cmd,
        db_queries=mock_db_queries,
        proz_client_port=mock_proz_client_port,
        jwt_port=mock_jwt_port,
    )


async def test_handle_create_token_via_proz_event(
    services: TokenCreateService,
) -> None:
    request = ProzCode(code="test_code")
    fixed_refresh_token = uuid.uuid4()

    with patch(
        "app.domain.events.token_created.uuid4",
        return_value=fixed_refresh_token,
    ):
        result = await handle_create_token_via_proz_event(request, services)

    assert isinstance(result, Tokens)

    expected_proz_access_token = (
        services.proz_client_port.exchange_code_for_tokens.return_value.access_token
    )
    expected_proz_refresh_token = (
        services.proz_client_port.exchange_code_for_tokens.return_value.refresh_token
    )
    expected_proz_user_info = services.proz_client_port.get_token_owner.return_value
    expected_user_id = services.db_queries.get_user_id_by_proz_id.return_value

    services.proz_client_port.exchange_code_for_tokens.assert_called_once_with(
        request.code,
    )
    services.proz_client_port.get_token_owner.assert_called_once_with(
        expected_proz_access_token,
    )
    services.db_queries.get_user_id_by_proz_id.assert_called_once_with(
        expected_proz_user_info.id,
    )
    services.jwt_port.create_token.assert_called_once_with(expected_user_id)
    services.db_cmd.upsert_proz_user.assert_called_once_with(
        expected_user_id,
        expected_proz_user_info,
        expected_proz_refresh_token,
    )
    services.db_cmd.refresh_session.assert_called_once_with(
        expected_user_id,
        fixed_refresh_token,
    )

    assert result.refresh_token == fixed_refresh_token
