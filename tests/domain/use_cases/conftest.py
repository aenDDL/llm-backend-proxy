from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from app.domain.models import ProzMembership, ProzUser, Tokens
from app.domain.ports import (
    AuthCommandPort,
    AuthQueryPort,
    ClockPort,
    TokenServicePort,
)


@pytest.fixture
def test_tokens() -> Tokens:
    test_access_token = "39718769-b1ee-459a-9d52-99f943e071d5"
    test_refresh_token = "a314cfc1-48ac-48c9-aaa2-8741790f932f"
    return Tokens(test_access_token, test_refresh_token)


@pytest.fixture
def test_user() -> ProzUser:
    membership = MagicMock(spec=ProzMembership)
    membership.ensure_active = MagicMock(return_value=None)

    user_id = UUID("7f366a19-5bd2-4f6a-8991-e2494ef6ff0d")
    return ProzUser(user_id, "test_user", "test_user@mail.com", membership)


@pytest.fixture
def mock_auth_cmd() -> AsyncMock:
    return AsyncMock(spec=AuthCommandPort)


@pytest.fixture
def mock_auth_query(test_user: ProzUser) -> AsyncMock:
    test_auth_query = AsyncMock(spec=AuthQueryPort)
    test_auth_query.get_token_owner = AsyncMock(return_value=test_user.id)
    test_auth_query.get_proz_status_info = AsyncMock(return_value=test_user.membership)
    return test_auth_query


@pytest.fixture
def mock_token_service(test_tokens: Tokens) -> MagicMock:
    test_token_service = MagicMock(spec=TokenServicePort)
    test_token_service.generate_token_pair = MagicMock(return_value=test_tokens)
    return test_token_service


@pytest.fixture
def mock_clock() -> MagicMock:
    test_clock = MagicMock(spec=ClockPort)
    test_clock.now = MagicMock(return_value=date(2027, 6, 6))
    return test_clock
