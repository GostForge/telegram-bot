"""/status handler — check current conversion status."""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..client import BackendClient
from ..texts import (
    STATUS_NO_JOBS, STATUS_NOT_FOUND, STATUS_ERROR,
    STATUS_JOB_COMPLETED, STATUS_JOB_FAILED, STATUS_JOB_PENDING,
    STATUS_JOB_IN_PROGRESS,
)

logger = logging.getLogger(__name__)
router = Router(name="status")

_client: BackendClient | None = None


def _get_client() -> BackendClient:
    global _client
    if _client is None:
        _client = BackendClient()
    return _client


@router.message(Command("status"))
async def cmd_status(message: Message, state: FSMContext):
    """Check status of the last conversion job."""
    data = await state.get_data()
    job_id = data.get("last_job_id")

    if not job_id:
        await message.answer(STATUS_NO_JOBS)
        return

    client = _get_client()
    try:
        status = await client.get_job_status(job_id)
    except Exception as e:
        if "404" in str(e):
            await message.answer(STATUS_NOT_FOUND)
        else:
            await message.answer(STATUS_ERROR.format(msg=str(e)[:200]))
        return

    current = status.get("status", "UNKNOWN")
    queue_pos = status.get("queuePosition")
    fmt = status.get("outputFormat", "DOCX")
    err_msg = status.get("errorMessage")

    if current == "COMPLETED":
        text = STATUS_JOB_COMPLETED.format(fmt=fmt, job_id=job_id)
    elif current == "FAILED":
        text = STATUS_JOB_FAILED.format(err=err_msg or "неизвестна")
    elif current == "PENDING":
        pos = f" (позиция: {queue_pos})" if queue_pos else ""
        text = STATUS_JOB_PENDING.format(pos=pos, fmt=fmt)
    else:
        text = STATUS_JOB_IN_PROGRESS.format(status=current, fmt=fmt)

    await message.answer(text)
