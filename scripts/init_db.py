import asyncio
import logging
from src.db.base import engine, Base
import src.db.models  # Load all SQLAlchemy models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_supabase():
    logger.info("Connecting to Supabase PostgreSQL and creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("All 13 tables successfully created in Supabase PostgreSQL!")


if __name__ == "__main__":
    asyncio.run(init_supabase())
