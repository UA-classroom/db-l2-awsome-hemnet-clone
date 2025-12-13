from .users import router as users_router
from .agencies import router as agencies_router
from .agents import router as agents_router
from .listings import router as listings_router
from .properties import router as properties_router
from .token import router as token_router

all_routers = [
    users_router,
    agencies_router,
    agents_router,
    listings_router,
    properties_router,
    token_router,
]
