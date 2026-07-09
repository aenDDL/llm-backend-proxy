from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.api.middleware.limiter import limiter
from app.domain.use_cases.exchange_token import CodeExchangeUseCase, exchange_token
from app.domain.use_cases.refresh_token import TokenRefreshUseCase, refresh_token

router = APIRouter(route_class=DishkaRoute, prefix="/oauth")


class AuthCodeIn(BaseModel):
    code: str


class RefreshTokenIn(BaseModel):
    token: str


class TokensOut(BaseModel):
    access: str
    refresh: str


@router.post("/token", response_model=TokensOut)
@limiter.limit("5/minute")
async def exchange_code_endpoint(
    request: Request,
    payload: AuthCodeIn,
    use_case: FromDishka[CodeExchangeUseCase],
):
    result = await exchange_token(
        code=payload.code,
        use_case=use_case,
    )
    return TokensOut(access=result.access_token, refresh=result.refresh_token)


@router.post("/refresh", response_model=TokensOut)
@limiter.limit("5/minute")
async def refresh_token_endpoint(
    request: Request,
    payload: RefreshTokenIn,
    use_case: FromDishka[TokenRefreshUseCase],
):
    result = await refresh_token(
        plain_refresh_token=payload.token,
        use_case=use_case,
    )
    return TokensOut(access=result.access_token, refresh=result.refresh_token)
