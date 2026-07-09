from pathlib import Path

from pydantic import BaseModel, PostgresDsn, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class ProzConfig(BaseModel):
    token_url: str
    user_url: str
    proz_redirect_uri: str
    proz_client_id: str
    proz_client_secret: SecretStr


class XaiConfig(BaseModel):
    model: str
    xai_api_key: SecretStr


class AnthropicConfig(BaseModel):
    model: str
    anthropic_api_key: SecretStr


class OpenAIConfig(BaseModel):
    model: str
    openai_api_key: SecretStr


class GoogleConfig(BaseModel):
    model: str
    google_api_key: SecretStr


class MistralConfig(BaseModel):
    model: str
    mistral_api_key: SecretStr


class CryptographyConfig(BaseModel):
    secret_key_to_hash: SecretStr
    secret_key_to_encrypt: SecretStr


class TokensConfig(BaseModel):
    secret_key: SecretStr
    access_token_expire_minutes: int
    algorithm: str


class DatabaseConfig(BaseModel):
    pg_dsn: PostgresDsn
    pg_pool_min_size: int
    pg_pool_max_size: int
    sql_dir: Path


class NetworkConfig(BaseModel):
    timeout: float


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        yaml_file="config.yaml",
        extra="ignore",
    )

    db: DatabaseConfig

    xai: XaiConfig
    anthropic: AnthropicConfig
    openai: OpenAIConfig
    google: GoogleConfig
    mistral: MistralConfig

    proz: ProzConfig
    cryptography: CryptographyConfig
    tokens: TokensConfig
    network: NetworkConfig

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        yaml_settings = YamlConfigSettingsSource(settings_cls)
        return init_settings, env_settings, dotenv_settings, yaml_settings

    @property
    def db_url(self) -> str:
        return str(self.db.pg_dsn)

    @property
    def sql_path(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent / self.db.sql_dir
