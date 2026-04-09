"""
HTTP client for GostForge backend Internal API.
Uses X-Internal-Api-Key + X-Telegram-Chat-Id for auth.
"""

import httpx
import logging

from .config import settings

logger = logging.getLogger(__name__)


class BackendClient:
    """Async httpx client for GostForge internal API."""

    def __init__(self):
        self._base = settings.backend_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    def _headers(self, chat_id: int | None = None) -> dict[str, str]:
        h = {"X-Internal-Api-Key": settings.internal_api_key}
        if chat_id is not None:
            h["X-Telegram-Chat-Id"] = str(chat_id)
        return h

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(300.0))
        return self._client

    # ── Conversion ────────────────────────────────────

    async def submit_conversion(
        self, chat_id: int, file_bytes: bytes, filename: str, output_format: str
    ) -> dict:
        """POST /api/v1/conversions — submit a conversion job (ZIP archive)."""
        import json as _json
        client = await self._get_client()
        options = _json.dumps({"outputFormat": output_format, "syntaxHighlighting": True})
        resp = await client.post(
            f"{self._base}/api/v1/conversions",
            headers=self._headers(chat_id),
            files={"archive": (filename, file_bytes, "application/zip")},
            data={"options": options},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_job_status(self, job_id: str) -> dict:
        """GET /api/v1/conversions/jobs/{jobId}"""
        client = await self._get_client()
        resp = await client.get(
            f"{self._base}/api/v1/conversions/{job_id}",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    async def download_result(self, job_id: str, fmt: str) -> bytes:
        """GET /api/v1/conversions/jobs/{jobId}/download/{format}"""
        client = await self._get_client()
        resp = await client.get(
            f"{self._base}/api/v1/conversions/{job_id}/result",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.content

    # ── Telegram linking ──────────────────────────────

    async def verify_link(self, code: str, chat_id: int) -> dict:
        """POST /internal/telegram/verify-link"""
        client = await self._get_client()
        resp = await client.post(
            f"{self._base}/internal/telegram/verify-link",
            headers=self._headers(),
            json={"code": code, "telegramChatId": chat_id},
        )
        resp.raise_for_status()
        return resp.json()

    async def mini_app_auth(self, init_data: str) -> dict:
        """POST /internal/telegram/mini-app-auth"""
        client = await self._get_client()
        resp = await client.post(
            f"{self._base}/internal/telegram/mini-app-auth",
            headers=self._headers(),
            json={"initData": init_data},
        )
        resp.raise_for_status()
        return resp.json()

    # ── Health ────────────────────────────────────────

    async def health_check(self) -> bool:
        try:
            client = await self._get_client()
            resp = await client.get(f"{self._base}/actuator/health")
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
