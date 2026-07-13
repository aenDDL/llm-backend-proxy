from dataclasses import dataclass
from datetime import date
from functools import partial
from uuid import UUID

from httpx import AsyncClient
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from app.adapters.http_client import DTO, fetch_request
from app.domain.models import ProzMembership as DomainProzMembership
from app.domain.models import ProzUser as DomainProzUser
from app.domain.models import Tokens


class Membership(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str | None = Field(alias="membership_type", default=None)
    expire_on: date | None = Field(alias="expiration_date", default=None)


class ProzUser(DTO):
    model_config = ConfigDict(populate_by_name=True)

    proz_id: UUID = Field(alias="uuid")
    name: str = Field(alias="site_name")
    email: EmailStr | None = Field(default=None)
    membership: Membership = Field(alias="proz_membership")

    def to_domain(self) -> DomainProzUser:
        membership = (
            DomainProzMembership(self.membership.type, self.membership.expire_on)
            if self.membership.type and self.membership.expire_on
            else None
        )
        return DomainProzUser(
            id=self.proz_id,
            name=self.name,
            email=self.email,
            membership=membership,
        )


class ProzTokens(DTO):
    access_token: str
    refresh_token: str

    def to_domain(self) -> Tokens:
        return Tokens(access_token=self.access_token, refresh_token=self.refresh_token)


@dataclass
class ProzClient:
    http_client: AsyncClient
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    user_url: str
    token_url: str

    async def exchange_code_for_tokens(self, code: str) -> Tokens:
        request = partial(
            self.http_client.post,
            url=self.token_url,
            auth=(self.client_id, self.client_secret.get_secret_value()),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            },
        )
        return await fetch_request(
            request=request,
            expected_response_model=ProzTokens,
        )

    async def get_token_owner(self, access_token: str) -> DomainProzUser:
        request = partial(
            self.http_client.get,
            url=self.user_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return await fetch_request(
            request=request,
            expected_response_model=ProzUser,
        )
