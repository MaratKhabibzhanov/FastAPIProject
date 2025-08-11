from secrets import compare_digest

from fastapi import HTTPException, status
from passlib.hash import bcrypt

from src.models.models import fake_users_db
from src.schemas import User, UserInDB


def authenticate_user(user: User):
    user_in_db: UserInDB = get_user_from_db(user.username)
    if user_in_db is None or not bcrypt.verify(user.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_in_db


def get_user_from_db(username: str):
    for user in fake_users_db:
        if compare_digest(user.username, username):
            return user
    return None


def create_new_user(user: User):
    new_user = UserInDB(username=user.username, hashed_password=bcrypt.hash(user.password))
    fake_users_db.append(new_user)
