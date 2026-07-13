from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from app.domain.errors import UnauthorizedError

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID


@dataclass(frozen=True)
class Tokens:
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class ProzMembership:
    membership: str | None = field(default=None)
    expire_on: date | None = field(default=None)

    def has_type(self) -> bool:
        return bool(self.membership)

    def is_expired(self, today: date) -> bool:
        return self.expire_on is None or self.expire_on < today

    def is_active(self, today: date) -> bool:
        return self.has_type() and not self.is_expired(today)

    def ensure_active(self, today: date) -> None:
        if not self.has_type():
            msg = "Membership has no type assigned"
            raise UnauthorizedError(msg)
        if self.is_expired(today):
            msg = "Membership has expired"
            raise UnauthorizedError(msg)


@dataclass(frozen=True)
class ProzUser:
    id: UUID
    name: str
    email: str | None = field(default=None)
    membership: ProzMembership | None = field(default=None)


@dataclass(frozen=True)
class ChatPrompts:
    owner: UUID
    system_prompt: str
    user_prompt: str


@dataclass
class ChatDetails:
    model: str
    cost_usd: Decimal
    tokens_total: int

    def __post_init__(self) -> None:
        self.cost_usd = Decimal(str(self.cost_usd))
