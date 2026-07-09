from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka, inject
from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.sse import EventSourceResponse
from pydantic import BaseModel, Field

from app.api.dependencies.ai_models import AvailableChat
from app.api.middleware.limiter import limiter
from app.domain.models import ChatPrompts
from app.domain.ports import TokenServicePort
from app.domain.use_cases.stream_chat_response import ChatUseCase, stream_chat_response

router = APIRouter(prefix="/api/v1", route_class=DishkaRoute)

bearer_scheme = HTTPBearer()


class UserRequestIn(BaseModel):
    system_prompt: str = Field(max_length=4000)
    user_prompt: str = Field(max_length=8000)


@inject
async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    token_service: FromDishka[TokenServicePort],
) -> UUID:
    """Verify JWT and return user ID.

    Raises:
        UnauthorizedError: if token unverified

    """
    return token_service.verify_token(credentials.credentials)


@router.post(
    "/chat/completions/{provider}",
    response_class=EventSourceResponse,
)
@limiter.limit("5/minute")
async def chat_endpoint(
    request: Request,
    provider: AvailableChat,
    payload: UserRequestIn,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: FromDishka[ChatUseCase],
):
    domain = ChatPrompts(
        owner=user_id,
        system_prompt=payload.system_prompt,
        user_prompt=payload.user_prompt,
    )
    async for chunk in stream_chat_response(prompts=domain, use_case=use_case):
        yield chunk
