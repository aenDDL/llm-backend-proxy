import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain.errors import (
    UnauthorizedError,
    UnavailableError,
)

logger = logging.getLogger(__name__)


async def unanvailable_error_handler(
    _request: Request,
    exc: UnavailableError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )


async def unauthorized_error_handler(
    _request: Request,
    _exc: UnauthorizedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Unauthorized"},
    )
