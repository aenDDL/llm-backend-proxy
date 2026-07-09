from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.dependencies import (
    provide_ai,
    provide_deps,
    provide_repositories,
    provide_use_cases,
)
from app.api.middleware.limiter import limiter
from app.api.v1 import auth, chat
from app.domain.errors import (
    UnauthorizedError,
    UnavailableError,
)
from app.infrastructure.errors import (
    unanvailable_error_handler,
    unauthorized_error_handler,
)

container = make_async_container(
    *provide_deps(),
    *provide_ai(),
    provide_repositories(),
    provide_use_cases(),
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await app.state.dishka_container.close()


app = FastAPI(lifespan=lifespan)

setup_dishka(container, app=app)

app.state.limiter = limiter

app.include_router(auth.router, tags=["auth"])
app.include_router(chat.router, tags=["chat"])

app.add_exception_handler(UnauthorizedError, unauthorized_error_handler)
app.add_exception_handler(UnavailableError, unanvailable_error_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health", tags=["health"])
def read_root():
    return "Server is running."
