from collections.abc import AsyncGenerator
from dataclasses import dataclass, field

from genai_prices import calc_price
from pydantic_ai import Agent
from pydantic_ai.result import StreamedRunResult

from app.domain.models import ChatDetails, ChatPrompts


@dataclass
class ChatService:
    agent: Agent
    chat: StreamedRunResult | None = field(default=None, init=False)

    def _get_model_name(self) -> str:
        messages = self.chat.all_messages()
        response = messages[-1]
        return response.model_name

    async def run_stream(self, prompts: ChatPrompts) -> AsyncGenerator[str, None]:
        async with self.agent.run_stream(
            user_prompt=prompts.user_prompt,
            instructions=prompts.system_prompt,
        ) as chat:
            async for chunk in chat.stream_text(delta=True):
                yield chunk
            self.chat = chat

    def get_details(self) -> ChatDetails:
        usage = self.chat.usage
        model = self._get_model_name()
        return ChatDetails(
            model=model,
            tokens_total=usage.total_tokens,
            cost_usd=calc_price(usage=usage, model_ref=model).total_price,
        )
