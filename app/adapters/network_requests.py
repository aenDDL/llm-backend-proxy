from collections.abc import Awaitable, Callable
from json import JSONDecodeError
from typing import Any

from httpx import URL, HTTPStatusError, RequestError, Response
from pydantic import BaseModel, ValidationError

from app.domain.errors import UnauthorizedError, UnavailableError


def _to_json(e: HTTPStatusError) -> dict | None:
    try:
        decoded = e.response.json()
        return decoded if isinstance(decoded, dict) else None
    except JSONDecodeError:
        return None


def _raise_for_httpx_error(e: HTTPStatusError | RequestError, url: URL) -> None:
    if isinstance(e, RequestError):
        raise UnavailableError(
            message=f"Service from {url} unavailable",
            details=str(e),
        )

    content = _to_json(e)
    if content is not None and content.get("error") == "invalid_grant":
        raise UnauthorizedError(details=str(e))

    raise UnavailableError(
        message=f"Service from {url} returned {e.response.status_code}",
        details=e.response.text,
        status=e.response.status_code,
    )


async def fetch_request(request: Callable[[], Awaitable[Response]]) -> Response:
    try:
        response = await request()
        response.raise_for_status()
    except (RequestError, HTTPStatusError) as e:
        _raise_for_httpx_error(e=e, url=e.request.url)
    return response


def validate_response[T: BaseModel](response: Response, model: type[T]) -> Any:
    try:
        return model.model_validate(response.json())
    except (ValidationError, JSONDecodeError) as e:
        raise UnavailableError(
            message=f"Unexpected response from {response.url}",
            details=str(e),
        ) from e


async def get_response[T: BaseModel](
    request: Callable[[], Awaitable[Response]],
    expected_response_model: type[T],
) -> T:
    response = await fetch_request(request=request)
    return validate_response(response=response, model=expected_response_model)
