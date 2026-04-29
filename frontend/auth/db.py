from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from frontend.auth.models import Base


def make_engine(db_url: str):
    return create_async_engine(db_url, future=True)


def make_session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
