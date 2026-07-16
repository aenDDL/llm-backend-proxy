from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest

from app.domain.ports import ChatCommandPort, ChatServicePort
from app.domain.use_cases.stream_chat_response import (
    ChatPrompts,
    ChatUseCase,
    stream_chat_response,
)


@pytest.fixture
def mock_chat_use_case() -> ChatUseCase:
    return ChatUseCase(
        chat=AsyncMock(spec=ChatServicePort),
        db=AsyncMock(spec=ChatCommandPort),
    )


async def test_stream_chat_response(mock_chat_use_case: ChatUseCase) -> None:
    use_case = mock_chat_use_case
    prompts = ChatPrompts(owner="user-1", system_prompt="test", user_prompt="test")

    async def fake_stream(*, prompts: ChatPrompts) -> AsyncGenerator[str, None]:  # ruff:ignore[unused-function-argument]
        for chunk in ("Hello", " ", "world"):
            yield chunk

    use_case.chat.run_stream.side_effect = fake_stream

    chunks = [chunk async for chunk in stream_chat_response(prompts, use_case)]

    assert chunks == ["Hello", " ", "world"]

    use_case.chat.run_stream.assert_called_once_with(prompts=prompts)
    use_case.chat.get_details.assert_called_once()
    use_case.db.save_chat_details.assert_awaited_once_with(
        user_id=prompts.owner,
        details=use_case.chat.get_details.return_value,
    )
