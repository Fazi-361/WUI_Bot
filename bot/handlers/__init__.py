from .start import start_router
from .help import help_router
from .settings import settings_router
from .info import info_router
from .id import id_router
from .message import message_router

ROUTERS = [
    start_router,
    help_router,
    settings_router,
    info_router,
    id_router,
    message_router # lasciare come ultimo
]

__all__ = [
    "ROUTERS",
]