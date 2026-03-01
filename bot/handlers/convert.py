"""/convert, /pdf, /both handlers — FSM-based conversion flow."""

import asyncio
import logging

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile

from ..client import BackendClient
from ..config import settings
from ..services import download_file, wrap_md_in_zip
from ..states import ConvertStates
from ..texts import (
    CONVERT_PROMPT, CONVERT_BAD_EXT, CONVERT_TOO_BIG,
    CONVERT_DOWNLOADING, CONVERT_SUBMITTING,
    CONVERT_NOT_LINKED, CONVERT_ACTIVE_JOB, CONVERT_ERROR,
    CONVERT_EXPECT_FILE, CONVERT_DONE_SENDING, CONVERT_TIMEOUT,
    CONVERT_FAILED, CONVERT_DELIVERY_FAIL,
    STATUS_PENDING, STATUS_PENDING_POS, STATUS_MERGING_MD,
    STATUS_CONVERTING_DOCX, STATUS_CONVERTING_PDF,
    STATUS_COMPLETED, STATUS_FAILED, STATUS_UNKNOWN,
)

logger = logging.getLogger(__name__)
router = Router(name="convert")

_FMT_LABELS = {"DOCX": "DOCX", "PDF": "PDF", "BOTH": "DOCX + PDF"}

_client: BackendClient | None = None


def _get_client() -> BackendClient:
    global _client
    if _client is None:
        _client = BackendClient()
    return _client


# ── Conversion commands ──────────────────────────────

@router.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext):
    """Start DOCX conversion flow."""
    await state.update_data(output_format="DOCX")
    await state.set_state(ConvertStates.waiting_file)
    await message.answer(CONVERT_PROMPT.format(fmt=_FMT_LABELS["DOCX"]))


@router.message(Command("pdf"))
async def cmd_pdf(message: Message, state: FSMContext):
    """Start PDF conversion flow."""
    await state.update_data(output_format="PDF")
    await state.set_state(ConvertStates.waiting_file)
    await message.answer(CONVERT_PROMPT.format(fmt=_FMT_LABELS["PDF"]))


@router.message(Command("both"))
async def cmd_both(message: Message, state: FSMContext):
    """Start DOCX+PDF conversion flow."""
    await state.update_data(output_format="BOTH")
    await state.set_state(ConvertStates.waiting_file)
    await message.answer(CONVERT_PROMPT.format(fmt=_FMT_LABELS["BOTH"]))


# ── File handler (in FSM state) ─────────────────────

@router.message(ConvertStates.waiting_file, F.document)
async def handle_file(message: Message, state: FSMContext, bot: Bot):
    """Receive file and start conversion."""
    doc = message.document
    data = await state.get_data()
    output_format = data.get("output_format", "DOCX")

    # Validate extension
    fname = doc.file_name or ""
    if not (fname.endswith(".md") or fname.endswith(".zip")):
        await message.answer(CONVERT_BAD_EXT)
        return

    # Validate size
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if doc.file_size and doc.file_size > max_bytes:
        await message.answer(
            CONVERT_TOO_BIG.format(
                size=doc.file_size // 1024 // 1024,
                limit=settings.max_file_size_mb,
            )
        )
        await state.clear()
        return

    # Download
    status_msg = await message.answer(CONVERT_DOWNLOADING)
    file_bytes, _ = await download_file(bot, doc.file_id)

    # Wrap single .md in zip
    if fname.endswith(".md"):
        file_bytes = wrap_md_in_zip(file_bytes, fname)
        fname = fname.replace(".md", ".zip")

    # Submit to backend
    await status_msg.edit_text(CONVERT_SUBMITTING)
    client = _get_client()
    chat_id = message.chat.id

    try:
        job = await client.submit_conversion(chat_id, file_bytes, fname, output_format)
    except Exception as e:
        error_msg = str(e)
        if "not linked" in error_msg.lower() or "403" in error_msg:
            await status_msg.edit_text(CONVERT_NOT_LINKED)
        elif "ACTIVE_JOB" in error_msg or "409" in error_msg:
            await status_msg.edit_text(CONVERT_ACTIVE_JOB)
        else:
            logger.exception("Submit failed for chat %s", chat_id)
            await status_msg.edit_text(CONVERT_ERROR.format(msg=error_msg[:200]))
        await state.clear()
        return

    job_id = job.get("jobId")
    await state.update_data(last_job_id=job_id)
    await state.clear()  # leave FSM, keep data for /status

    # Poll for completion
    await _poll_and_deliver(message, status_msg, client, job_id, output_format, bot)


@router.message(ConvertStates.waiting_file)
async def handle_non_document(message: Message):
    """User sent something other than a document in conversion mode."""
    await message.answer(CONVERT_EXPECT_FILE)


# ── Polling + delivery ───────────────────────────────

async def _poll_and_deliver(
    message: Message,
    status_msg: Message,
    client: BackendClient,
    job_id: str,
    output_format: str,
    bot: Bot,
):
    """Poll job status and send result files."""
    last_status = ""
    for _ in range(120):  # max ~2 min polling
        await asyncio.sleep(1.5)
        try:
            status = await client.get_job_status(job_id)
        except Exception:
            continue

        current = status.get("status", "")
        if current != last_status:
            last_status = current
            status_text = _status_to_text(current, status.get("queuePosition"))
            try:
                await status_msg.edit_text(status_text)
            except Exception:
                pass

        if current == "COMPLETED":
            try:
                await status_msg.edit_text(CONVERT_DONE_SENDING)
            except Exception:
                pass
            await _send_results(message, client, job_id, output_format)
            # Show conversion warnings to help user fix their report
            warnings = status.get("warnings")
            if warnings:
                warn_text = "⚠️ <b>Предупреждения конвертации:</b>\n"
                for w in warnings[:20]:  # limit to 20
                    warn_text += f"• {w}\n"
                if len(warnings) > 20:
                    warn_text += f"… и ещё {len(warnings) - 20}\n"
                await message.answer(warn_text)
            try:
                await status_msg.delete()
            except Exception:
                pass
            return

        if current == "FAILED":
            err = status.get("errorMessage", "Неизвестная ошибка")
            try:
                await status_msg.edit_text(CONVERT_FAILED.format(err=err[:300]))
            except Exception:
                pass
            return

    # Timeout
    try:
        await status_msg.edit_text(CONVERT_TIMEOUT)
    except Exception:
        pass


async def _send_results(
    message: Message, client: BackendClient, job_id: str, output_format: str
):
    """Download and send result files."""
    try:
        if output_format in ("DOCX", "BOTH"):
            docx_bytes = await client.download_result(job_id, "docx")
            await message.answer_document(
                BufferedInputFile(docx_bytes, filename="output.docx")
            )

        if output_format in ("PDF", "BOTH"):
            pdf_bytes = await client.download_result(job_id, "pdf")
            await message.answer_document(
                BufferedInputFile(pdf_bytes, filename="result.pdf")
            )
    except Exception as e:
        logger.exception("Failed to deliver results for job %s", job_id)
        await message.answer(CONVERT_DELIVERY_FAIL.format(err=str(e)[:200]))


def _status_to_text(status: str, queue_pos: int | None = None) -> str:
    mapping = {
        "PENDING": STATUS_PENDING_POS.format(pos=queue_pos) if queue_pos else STATUS_PENDING,
        "MERGING_MD": STATUS_MERGING_MD,
        "CONVERTING_DOCX": STATUS_CONVERTING_DOCX,
        "CONVERTING_PDF": STATUS_CONVERTING_PDF,
        "COMPLETED": STATUS_COMPLETED,
        "FAILED": STATUS_FAILED,
    }
    return mapping.get(status, STATUS_UNKNOWN.format(status=status))
