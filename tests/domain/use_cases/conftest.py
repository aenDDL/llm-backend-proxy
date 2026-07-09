import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.ports import (
    DatabaseCommandPort,
    DatabaseQueryPort,
    JWTPort,
)


@pytest.fixture
def mock_db_cmd() -> AsyncMock:
    return AsyncMock(spec=DatabaseCommandPort)


@pytest.fixture
def mock_db_queries() -> AsyncMock:
    test_user_id = uuid.uuid4()
    db_query = AsyncMock(spec=DatabaseQueryPort)
    db_query.get_user_id_by_proz_id.return_value = test_user_id
    db_query.get_user_id_by_token.return_value = test_user_id
    return db_query


@pytest.fixture
def mock_jwt_port() -> AsyncMock:
    jwt_service = MagicMock(spec=JWTPort)
    jwt_service.create_token.return_value = "test_jwt_access_token"
    return jwt_service
