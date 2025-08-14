from fastapi import APIRouter, Request, Response, status

from src.limiter.limiter import limiter
from src.models.models import Refresh, User
from src.security.security import create_jwt_tokens, update_refresh_token
from src.security.utils import authenticate_user, create_new_user


auth = APIRouter()


@auth.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: User):
    user = User(username=data.username, password=data.password)
    authenticated_user = authenticate_user(user)
    access_token, refresh_token = create_jwt_tokens({"sub": authenticated_user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth.post("/refresh")
@limiter.limit("5/minute")
async def refresh(request: Request, data: Refresh):
    access_token, refresh_token = update_refresh_token(data.refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth.post("/register")
@limiter.limit("1/minute")
async def register(user: User, request: Request, response: Response):
    create_new_user(user)
    response.status_code = status.HTTP_201_CREATED
    return {"message": "New user created"}
