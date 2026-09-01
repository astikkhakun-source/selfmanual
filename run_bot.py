import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from sqlalchemy import text
from src.core.config import settings
from src.db.base import engine, Base
from src.telegram.handlers.assessment import router as assessment_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN.startswith("YOUR_"):
        logger.error(
            "TELEGRAM_BOT_TOKEN не установлен в .env! "
            "Пожалуйста, укажите ваш токен Telegram-бота в файле .env"
        )
        return

    # 1. Initialize DB tables & run column migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100);"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;"))
        except Exception as mig_err:
            logger.info(f"Database migration note: {mig_err}")

    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(assessment_router)

    # 2. Delete any old webhooks so polling works immediately
    logger.info("Удаление старых вебхуков и очистка очереди...")
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Запуск Telegram-бота (Long Polling)...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
