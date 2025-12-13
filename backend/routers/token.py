from fastapi import HTTPException, Depends, status, APIRouter
from schemas import Token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from helpers import (
    get_db,
    authenticate_user,
    create_access_token,
)

router = APIRouter()


@router.post("/token", response_model=Token)
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
