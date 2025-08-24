from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, BigInteger, JSON, Float, Integer, Index
from config import settings

engine = create_async_engine(settings.POSTGRES_DSN, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mint: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    symbol: Mapped[str | None] = mapped_column(String(32))
    metadata_uri: Mapped[str | None] = mapped_column(String(256))
    flags: Mapped[dict] = mapped_column(JSON, default={})  # no_mint, no_freeze, lp_burnt

class Tick(Base):
    __tablename__ = "ticks"
    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[int] = mapped_column(index=True)
    ts_ms: Mapped[int] = mapped_column(BigInteger, index=True)
    price: Mapped[float] = mapped_column(Float)
    mc: Mapped[float] = mapped_column(Float)
    liquidity: Mapped[float] = mapped_column(Float)
    buys: Mapped[int] = mapped_column(Integer, default=0)
    sells: Mapped[int] = mapped_column(Integer, default=0)

class Signal(Base):
    __tablename__ = "signals"
    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[int] = mapped_column(index=True)
    ts_ms: Mapped[int] = mapped_column(BigInteger, index=True)
    score: Mapped[float] = mapped_column(Float)
    reason: Mapped[dict] = mapped_column(JSON)

class SmartTrade(Base):
    __tablename__ = "smart_trades"
    id: Mapped[int] = mapped_column(primary_key=True)
    wallet: Mapped[str] = mapped_column(String(64), index=True)
    token_id: Mapped[int] = mapped_column(index=True)
    side: Mapped[str] = mapped_column(String(4))  # BUY/SELL
    amount: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    ts_ms: Mapped[int] = mapped_column(BigInteger, index=True)

Index("ticks_t_token_ts", Tick.token_id, Tick.ts_ms)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
