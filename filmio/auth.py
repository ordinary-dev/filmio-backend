"""
Module with useful functions for authorization.
Most of the time you need one function - `get_current_user`.
"""

from datetime import datetime, timedelta

from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .mongo import users

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = config('SECRET_KEY', default='LEAKED_KEY')
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class BaseUser(BaseModel):
    username: str
    name: str | None = None


class NewUser(BaseUser):
    """ Information sent when registering a new user """
    email: str
    password: str


class UserInDB(BaseUser):
    """ Representation of a user in the database """
    email: str
    hashed_password: str
    profile_photo_url: str


class UserOut(BaseUser):
    """
    Information returned to any user.
    This class should not contain sensitive information
    """
    profile_photo_url: str


class CurrentUser(UserOut):
    """ Information returned to the account owner """
    email: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def get_user(username: str) -> UserInDB:
    """
    Get a record from the database

    Returns:
    - `UserInDB` - the record from database

    Raises:
    - `ValueError` if username was not found
    """
    query = {'username': username}
    user = users.find_one(query)
    if not user:
        raise ValueError('Username was not found in db')
    return UserInDB(**user)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(weeks=52)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    A function that can be used when authorization is required.

    ```
    @app.get("/me")
    async def get_user_info(user: User = Depends(get_current_user)):
    ```

    Returns:
    - `UserInDB`

    Raises:
    - `HTTPException` if JWT token is invalid or username was not found
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as jwt_error:
        raise credentials_exception from jwt_error

    user = get_user(username=username)
    if user is None:
        raise credentials_exception

    return user
