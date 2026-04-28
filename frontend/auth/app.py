from fastapi import FastAPI
from frontend.auth.users import make_fastapi_users
from frontend.auth.schemas import UserRead, UserCreate, UserUpdate
from frontend.auth.email import MailBackend
from frontend.auth.settings import Settings


def build_app(*, get_session, settings: Settings, mail: MailBackend) -> FastAPI:
    app = FastAPI()
    fapi_users = make_fastapi_users(get_session, settings, mail)

    # Only mount the register router from fastapi-users.
    # /auth/login and /auth/logout are custom (Tasks 12 / 13) — needed for lockout
    # and remember-me. We deliberately skip get_auth_router to avoid duplicate-route
    # registration conflicts.
    app.include_router(
        fapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
    )
    # Users router (PATCH /users/{id}, GET /users/me) — useful for admin/account UI later.
    app.include_router(
        fapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
    )

    return app
