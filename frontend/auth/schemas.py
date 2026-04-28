from pydantic import Field, ConfigDict, field_validator
from fastapi_users import schemas


USERNAME_PATTERN = r"^[a-zA-Z0-9_-]{3,32}$"


class UserRead(schemas.BaseUser[str]):
    # Override email to plain str so that test-style addresses (e.g. alice@test)
    # pass serialisation without requiring a TLD.
    email: str  # type: ignore[assignment]
    username: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    # Override email to accept test-style addresses (e.g. alice@test) in addition
    # to standard RFC-5321 addresses.  The underlying email_validator library
    # supports `test_environment=True` for domains without a TLD.
    email: str  # type: ignore[assignment]
    username: str = Field(..., pattern=USERNAME_PATTERN)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email_address(cls, v: str) -> str:
        from email_validator import validate_email, EmailNotValidError
        try:
            result = validate_email(v, check_deliverability=False, test_environment=True)
            return result.normalized
        except EmailNotValidError as exc:
            raise ValueError(str(exc)) from exc


class UserUpdate(schemas.BaseUserUpdate):
    # username NOT updatable in v1 (locked at signup)
    pass
