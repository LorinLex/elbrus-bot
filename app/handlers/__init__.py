from .main import router as main_router
from .sport import router as sport_router
from .events import router as event_router

__all__ = ["main_router", "sport_router", "event_router"]
