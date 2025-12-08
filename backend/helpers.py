from typing import Optional
from psycopg2 import OperationalError, IntegrityError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from db import fetch_one
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from db_setup import get_connection
from schemas import (
    User,
    UserInDB,
    TokenData,
)

SECRET_KEY = "secret-to-change-when-you-go-live-with-this-script"
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    conection = get_connection()
    try:
        yield conection
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to Database",
        )
    finally:
        conection.close()


def raise_if_not_found(row, label: str):
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} not found"
        )
    return row


def handle_error(exc: IntegrityError, fallback: str = "Invalid data"):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=fallback
    ) from exc


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, connection) -> Optional[UserInDB]:
    user = fetch_one(
        connection,
        "SELECT id, email, password FROM users WHERE email = %s",
        (username,),
    )
    if not user:
        return None
    return UserInDB(
        username=user["email"],
        id=user["id"],
        hashed_password=user["password"],
    )


def authenticate_user(username: str, password: str, connection) -> Optional[UserInDB]:
    user = get_user(username, connection)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ==== Dependency for protection endpoints ====
async def get_current_user(
    token: str = Depends(oauth2_scheme), connection=Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload is None:
            raise credentials_exception

        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

        if token_data.username is None:
            raise credentials_exception

        user = get_user(username=token_data.username, connection=connection)
    except JWTError:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return user
