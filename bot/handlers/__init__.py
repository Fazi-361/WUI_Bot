from .start import start_router
from .help import help_router
from .settings import settings_router
from .info import info_router
from .id import id_router
from .deid import deid_router
from .hashes import hashes_router
from .message import message_router
from .random import random_router
from .my_chat_member import my_chat_member_router

from .random import random_router
ROUTERS = (
    start_router,
    help_router,
    settings_router,
    info_router,
    id_router,
    deid_router,
    hashes_router,
    random_router,
    message_router, # lasciare come ultimo
    
    my_chat_member_router,
)

__all__ = (
    "ROUTERS",
)
