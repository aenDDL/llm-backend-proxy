from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from pydantic import SecretStr

from app.domain.errors import UnauthorizedError
from app.domain.models import Tokens


@dataclass
class TokenService:
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int

    @staticmethod
    def _create_refresh_token() -> str:
        return str(uuid4())

    def _create_access_token(self, user_id: UUID) -> str:
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.now(UTC)
            + timedelta(minutes=self.access_token_expire_minutes),
        }
        return jwt.encode(
            to_encode,
            self.secret_key.get_secret_value(),
            algorithm=self.algorithm,
        )

    def generate_token_pair(self, user_id: UUID) -> Tokens:
        access = self._create_access_token(user_id)
        refresh = self._create_refresh_token()
        return Tokens(access_token=access, refresh_token=refresh)

    def verify_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(
                token,
                self.secret_key.get_secret_value(),
                algorithms=[self.algorithm],
                options={"require": ["exp", "sub"]},
            )
        except jwt.InvalidTokenError as e:
            msg = "Invalid JWT"
            raise UnauthorizedError(msg) from e
        else:
            return UUID(payload["sub"])
