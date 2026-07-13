from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from json import JSONDecodeError
from typing import Any

from httpx import HTTPStatusError, RequestError, Response
from pydantic import BaseModel, ValidationError

from app.adapters.transport_errors import raise_for_http_error
from app.domain.errors import UnavailableError


class DTO(BaseModel, ABC):
    @abstractmethod
    def to_domain(self) -> Any: ...


async def call_api(request: Callable[[], Awaitable[Response]]) -> Response:
    try:
        response = await request()
        response.raise_for_status()
    except (RequestError, HTTPStatusError) as e:
        raise_for_http_error(e=e, url=e.request.url)
    return response


def validate_response[T: DTO](response: Response, model: type[T]) -> T:
    try:
        return model.model_validate(response.json())
    except (ValidationError, JSONDecodeError) as e:
        raise UnavailableError(
            message=f"Unexpected response from {response.url}",
            details=str(e),
        ) from e


async def fetch_request[T: DTO](
    request: Callable[[], Awaitable[Response]],
    expected_response_model: type[T],
) -> Any:
    response = await call_api(request=request)
    validated_obj = validate_response(
        response=response,
        model=expected_response_model,
    )
    return validated_obj.to_domain()
