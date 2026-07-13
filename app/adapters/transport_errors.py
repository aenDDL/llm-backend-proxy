from json import JSONDecodeError
from typing import NoReturn

from httpx import URL, HTTPStatusError, RequestError

from app.domain.errors import UnauthorizedError, UnavailableError


def _to_json(e: HTTPStatusError) -> dict | None:
    try:
        decoded = e.response.json()
        return decoded if isinstance(decoded, dict) else None
    except JSONDecodeError:
        return None


def raise_for_http_error(e: HTTPStatusError | RequestError, url: URL) -> NoReturn:
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
