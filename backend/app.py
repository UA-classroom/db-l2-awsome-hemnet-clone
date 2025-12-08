from db_setup import run_setup
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from schemas import User, Token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from helpers import (
    get_db,
    authenticate_user,
    create_access_token,
)

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


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), connection=Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, connection)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token}
