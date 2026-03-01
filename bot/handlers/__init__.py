"""Handlers package — registers all routers."""

from aiogram import Router

from .start import router as start_router
from .link import router as link_router
from .convert import router as convert_router
from .status import router as status_router
from .unlink import router as unlink_router

router = Router(name="root")
router.include_router(start_router)
router.include_router(link_router)
router.include_router(convert_router)
router.include_router(status_router)
router.include_router(unlink_router)
