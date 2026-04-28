from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = Field(..., min_length=32)
    base_url: str

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_app_password: str
    mail_backend: Literal["smtp", "console"] = "smtp"

    admin_bootstrap_email: str

    auth_db_url: str = "sqlite+aiosqlite:///./auth.db"

    @property
    def secure_cookie(self) -> bool:
        return self.base_url.startswith("https://")


def load_settings() -> Settings:
    import os
    if not os.environ.get("ADMIN_BOOTSTRAP_EMAIL"):
        raise RuntimeError(
            "ADMIN_BOOTSTRAP_EMAIL is required at startup. "
            "Set it explicitly (use empty string only after considered review)."
        )
    return Settings()
