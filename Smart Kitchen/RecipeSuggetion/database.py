from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://meet_patel:1243@localhost:5432/kitchen_db"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, autocommit=False, autoflush=False)

Base = declarative_base()

async def create_tables():
    async with engine.begin() as conn:
        print("Creating tables...")  # Debugging
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")  # Debugging

async def get_db():
    async with SessionLocal() as session:
        yield session
