"""/unlink handler — unlink Telegram account.

Note: unlinking is done via the auth portal (user-facing /api/v1/users/me/telegram/unlink).
The bot just confirms intent and tells the user to unlink from the portal.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..texts import UNLINK_INFO

logger = logging.getLogger(__name__)
router = Router(name="unlink")


@router.message(Command("unlink"))
async def cmd_unlink(message: Message):
    """Tell user how to unlink their account."""
    await message.answer(UNLINK_INFO)
