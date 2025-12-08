from db_setup import run_setup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import all_routers


tags_metadata = [
    {
        "name": "listings",
        "description": "Operations with listings info.",
    },
    {
        "name": "properties",
        "description": "Operations with property info.",
    },
    {
        "name": "agents",
        "description": "Operations with agents info.",
    },
    {"name": "agencies", "description": "Operations with agencies info."},
    {
        "name": "users",
        "description": "Operations with users info.",
    },
]

app = FastAPI(title="Hemnet Clone API", version="1.0.0", openapi_tags=tags_metadata)

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

run_setup()

#########################################
#           SETUP ROUTERS               #
#########################################

for router in all_routers:
    app.include_router(router)
