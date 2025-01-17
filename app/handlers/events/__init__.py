from aiogram import Router
from .create import router as create_router
from .read import router as read_router
from .update import router as update_router
from .delete import router as delete_router

event_router = Router(name="event")
event_router.include_routers(
    create_router,
    read_router,
    update_router,
    delete_router
)
