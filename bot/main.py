"""
GostForge Telegram Bot entry point.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import settings
from .handlers import router
from .client import BackendClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)

_client: BackendClient | None = None


async def on_startup(bot: Bot):
    me = await bot.get_me()
    logger.info("Bot started: @%s (%s)", me.username, me.full_name)


async def on_shutdown(bot: Bot):
    global _client
    if _client:
        await _client.close()
    logger.info("Bot stopped")


async def run():
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting GostForge Telegram Bot...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
