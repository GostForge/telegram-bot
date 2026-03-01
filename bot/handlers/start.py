"""/start handler — welcome + Mini App button."""

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from ..config import settings
from ..texts import (
    START_BUTTON_LOGIN, START_WELCOME,
    START_LINK_STEP_MINIAPP, START_LINK_STEP_FALLBACK,
)

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Welcome message with Mini App auth button (HTTPS only)."""
    mini_app_url = settings.mini_app_url
    is_https = mini_app_url.startswith("https://")

    # Telegram requires HTTPS for WebApp buttons
    if is_https:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=START_BUTTON_LOGIN,
                web_app=WebAppInfo(url=mini_app_url),
            )],
        ])
    else:
        kb = None
        logger.warning(
            "MINI_APP_URL (%s) is not HTTPS — WebApp button disabled", mini_app_url
        )

    link_step = START_LINK_STEP_MINIAPP if is_https else START_LINK_STEP_FALLBACK
    await message.answer(
        START_WELCOME.format(link_step=link_step),
        reply_markup=kb,
    )
