import hashlib
import hmac
from dataclasses import dataclass
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from pydantic import SecretStr

from app.domain.errors import UnauthorizedError


@dataclass
class Hasher:
    secret_key: SecretStr

    def hash(self, data: str | UUID) -> str:
        return hmac.new(
            self.secret_key.get_secret_value().encode(),
            str(data).encode(),
            hashlib.sha256,
        ).hexdigest()


@dataclass
class Encrypter:
    secret_key: SecretStr

    def __post_init__(self) -> None:
        key = self.secret_key.get_secret_value().encode()
        self._fernet = Fernet(key)

    def encrypt(self, data: str | UUID) -> str:
        encrypted_bytes = self._fernet.encrypt(str(data).encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, encrypted: str) -> str:
        try:
            decrypted_bytes = self._fernet.decrypt(encrypted.encode("utf-8"))
            decoded = decrypted_bytes.decode("utf-8")
        except (InvalidToken, ValueError) as e:
            msg = "Invalid encrypted token or key"
            raise UnauthorizedError(msg) from e
        else:
            return decoded
