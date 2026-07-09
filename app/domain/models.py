from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID


@dataclass(frozen=True)
class Tokens:
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class ProzMembership:
    type: str
    expire_on: date


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
