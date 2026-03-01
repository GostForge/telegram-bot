"""File handling: download from TG, wrap single .md in ZIP if needed."""

import io
import zipfile
import logging

from aiogram import Bot

logger = logging.getLogger(__name__)


async def download_file(bot: Bot, file_id: str) -> tuple[bytes, str]:
    """Download a file from Telegram, return (bytes, file_name)."""
    file = await bot.get_file(file_id)
    buf = io.BytesIO()
    await bot.download_file(file.file_path, buf)
    return buf.getvalue(), file.file_path.split("/")[-1] if file.file_path else "file"


def wrap_md_in_zip(md_bytes: bytes, filename: str) -> bytes:
    """Wrap a single .md file in a ZIP archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, md_bytes)
    return buf.getvalue()


def is_zip(data: bytes) -> bool:
    """Check if data starts with ZIP magic bytes."""
    return data[:4] == b"PK\x03\x04"
