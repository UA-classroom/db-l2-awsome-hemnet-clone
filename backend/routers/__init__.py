from .users import router as users_router
from .agencies import router as agencies_router
from .agents import router as agents_router
from .listings import router as listings_router
from .properties import router as properties_router

all_routers = [
    users_router,
    agencies_router,
    agents_router,
    listings_router,
    properties_router,
]

# kör detta i app.py när du har fakturerat ut alla enpoints ur app.py
# from routers import all_routers
# for r in all_routers:
#     app.include_router(r)
