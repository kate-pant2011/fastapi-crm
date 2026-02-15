from app.config.config import settings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


engine = create_async_engine(
    settings.DATABASE_URL, 
    pool_recycle=3600,
    echo=True,
) 

# ленивое создание Session-объекта, подключение к БД происходит при первом SQL-запросе!
SessionLocal = async_sessionmaker(
    expire_on_commit=False,
    autoflush=False,
    bind=engine,
)

async def get_db():
    async with SessionLocal() as session:
        yield session
        await session.close()
