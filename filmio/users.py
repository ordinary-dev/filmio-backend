from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from .auth import (NewUser, CurrentUser, UserOut, UserInDB, get_user, verify_password,
                   create_access_token, get_current_user, get_password_hash)
from .mongo import users

users_router = APIRouter(tags=['users'])


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str):
    """
    Returns:
    - `UserInDB` - a record from the database about the user
    - `None` - the user does not exist or the password is invalid
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@users_router.post("/token", response_model=Token)
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get a JWT token.

    Raises:
    - `HTTPException` - incorrect username or password
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return Token(access_token=access_token, token_type="bearer")


@users_router.get("/me", response_model=CurrentUser)
async def get_user_info(current_user: UserInDB = Depends(get_current_user)):
    """ Returns information about the current user """
    return current_user


@users_router.get("/users/{username}", response_model=UserOut)
async def get_user_by_username(username: str):
    """
    Returns user information

    Raises:
    - `HTTPException` - the user doesn't exist
    """
    user = users.find_one({'username': username})
    if not user:
        raise HTTPException(404, 'User does not exist')
    return UserInDB(**user)


@users_router.post('/users', response_model=CurrentUser)
async def register(user: NewUser):
    """ Creates a new user """
    user_in_db = UserInDB(
        **user.dict(),
        hashed_password=get_password_hash(user.password)
    )
    users.insert_one(user_in_db.dict())
    return user_in_db
