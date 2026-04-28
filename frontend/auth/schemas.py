from pydantic import Field, ConfigDict
from fastapi_users import schemas


USERNAME_PATTERN = r"^[a-zA-Z0-9_-]{3,32}$"


class UserRead(schemas.BaseUser[str]):
    username: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(..., pattern=USERNAME_PATTERN)


class UserUpdate(schemas.BaseUserUpdate):
    # username NOT updatable in v1 (locked at signup)
    pass
