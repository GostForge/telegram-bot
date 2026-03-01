"""/link <code> handler — fallback account linking."""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..client import BackendClient
from ..texts import (
    LINK_USAGE, LINK_SUCCESS, LINK_INVALID_CODE,
    LINK_ALREADY_LINKED, LINK_ERROR,
)

logger = logging.getLogger(__name__)
router = Router(name="link")

_client: BackendClient | None = None


def _get_client() -> BackendClient:
    global _client
    if _client is None:
        _client = BackendClient()
    return _client


@router.message(Command("link"))
async def cmd_link(message: Message):
    """Link Telegram account using a code from the auth portal."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.answer(LINK_USAGE)
        return

    code = args[1].strip()
    chat_id = message.chat.id
    client = _get_client()

    try:
        result = await client.verify_link(code, chat_id)
        username = result.get("username", "")
        await message.answer(LINK_SUCCESS.format(username=username))
    except Exception as e:
        error_msg = str(e)
        if "INVALID_CODE" in error_msg or "expired" in error_msg.lower():
            await message.answer(LINK_INVALID_CODE)
        elif "CHAT_ALREADY_LINKED" in error_msg:
            await message.answer(LINK_ALREADY_LINKED)
        else:
            logger.exception("Link failed for chat %s", chat_id)
            await message.answer(LINK_ERROR.format(msg=error_msg[:200]))
