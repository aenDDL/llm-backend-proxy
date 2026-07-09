from collections.abc import AsyncGenerator
from dataclasses import dataclass

from app.domain.models import ChatPrompts
from app.domain.ports import ChatCommandPort, ChatServicePort


@dataclass(frozen=True)
class ChatUseCase:
    chat: ChatServicePort
    db: ChatCommandPort


async def stream_chat_response(
    prompts: ChatPrompts,
    use_case: ChatUseCase,
) -> AsyncGenerator[str, None]:
    """Streams response based on user prompts.

    Raises:
        UnavailableError: if any service is down

    """
    async for chunk in use_case.chat.run_stream(prompts=prompts):
        yield chunk

    details = use_case.chat.get_details()
    await use_case.db.save_chat_details(user_id=prompts.owner, details=details)
