import os
import datetime

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import sessionmaker, DeclarativeBase, MappedColumn, mapped_column
from sqlalchemy import Integer, String



POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "async")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(DB_URL)

DbSession = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass

class StarWarsPersons(Base):
    __tablename__ = "swpers"
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    sw_id: MappedColumn[int] = mapped_column(Integer)
    name: MappedColumn[str] = mapped_column(String)
    birth_year: MappedColumn[str] = mapped_column(String)
    eye_color: MappedColumn[str] = mapped_column(String)
    gender: MappedColumn[str] = mapped_column(String)
    hair_color: MappedColumn[str] = mapped_column(String)
    homeworld: MappedColumn[str] = mapped_column(String)
    mass: MappedColumn[str] = mapped_column(String)
    skin_color: MappedColumn[str] = mapped_column(String)

async def open_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_orm():
    await engine.dispose()