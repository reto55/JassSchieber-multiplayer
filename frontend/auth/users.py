from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
)
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
)
from sqlalchemy.ext.asyncio import AsyncSession

from frontend.auth.models import User, AccessToken
from frontend.auth.manager import UserManager
from frontend.auth.email import MailBackend
from frontend.auth.settings import Settings


def make_user_db_dep(get_session):
    async def get_user_db(session: AsyncSession = Depends(get_session)):
        yield SQLAlchemyUserDatabase(session, User)
    return get_user_db


def make_token_db_dep(get_session):
    async def get_token_db(session: AsyncSession = Depends(get_session)):
        yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
    return get_token_db


def make_manager_dep(get_session, settings: Settings, mail: MailBackend):
    user_db_dep = make_user_db_dep(get_session)

    async def get_user_manager(
        session: AsyncSession = Depends(get_session),
        user_db = Depends(user_db_dep),
    ):
        m = UserManager(user_db)
        m.settings = settings
        m.mail = mail
        m.db = session
        m.reset_password_token_secret = settings.secret_key
        m.verification_token_secret = settings.secret_key
        yield m
    return get_user_manager


def make_auth_backend(get_session, secure: bool) -> AuthenticationBackend:
    cookie = CookieTransport(
        cookie_name="schieber_session",
        cookie_max_age=2 * 60 * 60,
        cookie_secure=secure,
        cookie_httponly=True,
        cookie_samesite="lax",
    )
    token_db_dep = make_token_db_dep(get_session)

    def get_strategy(token_db = Depends(token_db_dep)) -> DatabaseStrategy:
        return DatabaseStrategy(token_db, lifetime_seconds=2 * 60 * 60)

    return AuthenticationBackend(
        name="cookie-db",
        transport=cookie,
        get_strategy=get_strategy,
    )


def make_fastapi_users(get_session, settings: Settings, mail: MailBackend):
    return FastAPIUsers[User, str](
        get_user_manager=make_manager_dep(get_session, settings, mail),
        auth_backends=[make_auth_backend(get_session, settings.secure_cookie)],
    )
