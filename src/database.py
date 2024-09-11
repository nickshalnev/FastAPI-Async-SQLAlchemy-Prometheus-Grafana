from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    engine = create_async_engine(DATABASE_URL, echo=True, future=True)
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
else:
    print("WARNING! NO DATABASE_URL")
Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session

