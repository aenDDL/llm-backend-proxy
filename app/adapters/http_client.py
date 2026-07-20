from __future__ import annotations

from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import TYPE_CHECKING, NoReturn

from httpx import HTTPStatusError, RequestError, Response
from pydantic import BaseModel, ValidationError

from app.domain.errors import UnauthorizedError, UnavailableError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from _typeshed import DataclassInstance


def _to_json(e: HTTPStatusError) -> dict | None:
    try:
        decoded = e.response.json()
        return decoded if isinstance(decoded, dict) else None
    except JSONDecodeError:
        return None


def _raise_request_error(exc: RequestError) -> NoReturn:
    raise UnavailableError(
        message=f"An error occurred while requesting {exc.request.url!r}.",
    ) from exc


def _raise_http_status_error(exc: HTTPStatusError) -> NoReturn:
    content = _to_json(exc)
    if content is not None and content.get("error") == "invalid_grant":
        raise UnauthorizedError(details=str(exc)) from exc
    raise UnavailableError(
        message=f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.",
    ) from exc


class DataTransfer[D: DataclassInstance](BaseModel, ABC):
    @abstractmethod
    def to_domain(self) -> D: ...


async def call_api(request: Callable[[], Awaitable[Response]]) -> Response:
    try:
        response = await request()
        response.raise_for_status()
    except RequestError as exc:
        _raise_request_error(exc)
    except HTTPStatusError as exc:
        _raise_http_status_error(exc)
    else:
        return response


def validate_response[T: DataTransfer](response: Response, model: type[T]) -> T:
    try:
        return model.model_validate(response.json())
    except (ValidationError, JSONDecodeError) as e:
        raise UnavailableError(
            message=f"Unexpected response from {response.url}",
            details=str(e),
        ) from e


async def fetch_request[T: DataclassInstance](
    request: Callable[[], Awaitable[Response]],
    expected_dto: type[DataTransfer[T]],
) -> T:
    response = await call_api(request=request)
    validated_obj = validate_response(
        response=response,
        model=expected_dto,
    )
    return validated_obj.to_domain()
