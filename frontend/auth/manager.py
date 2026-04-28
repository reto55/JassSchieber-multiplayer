from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets
from fastapi import Request
from fastapi_users import BaseUserManager, exceptions, InvalidPasswordException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from frontend.auth.models import User, EmailToken, Tombstone
from frontend.auth.passwords import validate_password
from frontend.auth.tombstone import hash_email, hash_username
from frontend.auth.email import (
    Mail,
    MailBackend,
    render_verification,
    render_reset,
)
from frontend.auth.settings import Settings


class UserManager(BaseUserManager[User, str]):
    reset_password_token_secret: str  # filled by factory in users.py
    verification_token_secret: str
    settings: Settings
    mail: MailBackend
    db: AsyncSession

    def parse_id(self, value) -> str:
        return str(value)

    async def validate_password(self, password: str, user) -> None:
        try:
            validate_password(
                password,
                username=getattr(user, "username", "") or "",
                email=getattr(user, "email", "") or "",
            )
        except Exception as exc:
            # Re-raise as fastapi-users' InvalidPasswordException so the register
            # router can catch it and return a proper 400 response.
            raise InvalidPasswordException(reason=str(exc)) from exc

    async def create(self, user_create, safe=False, request=None):
        # Check for duplicate username (fastapi-users only checks email)
        existing_username = (
            await self.db.execute(
                select(User).where(User.username == user_create.username)
            )
        ).scalars().first()
        if existing_username is not None:
            raise exceptions.UserAlreadyExists()

        # Block tombstone collisions <30d
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        eh = hash_email(user_create.email)
        uh = hash_username(user_create.username)
        q = select(Tombstone).where(
            ((Tombstone.email_hash == eh) | (Tombstone.username_hash == uh))
            & (Tombstone.deleted_at >= cutoff)
        )
        if (await self.db.execute(q)).scalars().first():
            raise exceptions.UserAlreadyExists()
        return await super().create(user_create, safe=safe, request=request)

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        token = secrets.token_urlsafe(32)
        et = EmailToken(
            token=token,
            user_id=user.id,
            purpose="verify",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.db.add(et)
        await self.db.commit()
        body = render_verification(
            username=user.username, base_url=self.settings.base_url, token=token
        )
        await self.mail.send(Mail(
            to=user.email,
            subject="Confirm your Schieber account",
            body=body,
        ))
        if user.email == self.settings.admin_bootstrap_email:
            await self.db.refresh(user)
            user.is_superuser = True
            user.is_verified = True   # bootstrap admin is trusted
            await self.db.commit()

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        # fastapi-users issues its own JWT token; we replace with our own DB-backed
        # token to keep audit + revocation simple
        new_token = secrets.token_urlsafe(32)
        et = EmailToken(
            token=new_token,
            user_id=user.id,
            purpose="reset",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        self.db.add(et)
        await self.db.commit()
        body = render_reset(
            username=user.username, base_url=self.settings.base_url, token=new_token
        )
        await self.mail.send(Mail(
            to=user.email,
            subject="Reset your Schieber password",
            body=body,
        ))
