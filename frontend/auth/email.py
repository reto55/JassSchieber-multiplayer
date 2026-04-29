from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Mail:
    to: str
    subject: str
    body: str


class MailBackend(Protocol):
    async def send(self, mail: Mail) -> None: ...


@dataclass
class ConsoleMailBackend:
    sent: list[Mail] = field(default_factory=list)

    async def send(self, mail: Mail) -> None:
        self.sent.append(mail)
        print(f"[mail] to={mail.to} subj={mail.subject}\n{mail.body}\n")


@dataclass
class SmtpMailBackend:
    host: str
    port: int
    user: str
    password: str

    async def send(self, mail: Mail) -> None:
        import aiosmtplib
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["From"] = self.user
        msg["To"] = mail.to
        msg["Subject"] = mail.subject
        msg.set_content(mail.body)
        await aiosmtplib.send(
            msg,
            hostname=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            start_tls=True,
        )


def render_verification(*, username: str, base_url: str, token: str) -> str:
    return (
        f"Hi {username},\n"
        f"Confirm your email within 7 days:\n"
        f"{base_url}/auth/verify?token={token}\n"
        f"If you didn't sign up, ignore this message.\n"
    )


def render_reset(*, username: str, base_url: str, token: str) -> str:
    return (
        f"Someone requested a password reset for {username}.\n"
        f"Click within 1 hour:\n"
        f"{base_url}/reset?token={token}\n"
        f"If this wasn't you, no action needed — your password is unchanged.\n"
    )


def render_change_email_confirm(*, base_url: str, token: str) -> str:
    return (
        f"Click to switch your account email:\n"
        f"{base_url}/auth/confirm-email?token={token}\n"
    )


def render_change_email_notice(*, masked_new_email: str) -> str:
    return (
        f"Someone requested to change your account email to {masked_new_email}.\n"
        f"If this wasn't you, change your password immediately.\n"
    )


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:3]}***@{domain}" if domain else email
