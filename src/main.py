from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, Header, Request, Response, status
from itsdangerous import BadSignature, URLSafeTimedSerializer

from src.models.models import cookie_cache
from src.schemas import CommonHeaders, Refresh, User

from .app import app, limiter
from .config import load_config as config
from .security import create_jwt_tokens, get_user_from_token, update_refresh_token
from .utils import authenticate_user, create_new_user, get_user_from_db


token_serializer = URLSafeTimedSerializer(secret_key=config().SECRET_KEY)


@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: User):
    user = User(username=data.username, password=data.password)
    authenticated_user = authenticate_user(user)
    access_token, refresh_token = create_jwt_tokens({"sub": authenticated_user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/refresh")
@limiter.limit("5/minute")
async def refresh(request: Request, data: Refresh):
    access_token, refresh_token = update_refresh_token(data.refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/register")
@limiter.limit("1/minute")
async def register(user: User, request: Request, response: Response):
    create_new_user(user)
    response.status_code = status.HTTP_201_CREATED
    return {"message": "New user created"}


@app.get("/protected_resource")
async def protected_resource(current_user: str = Depends(get_user_from_token)):
    """
    Этот маршрут защищен и требует токен. Если токен действителен, мы возвращаем информацию о пользователе.
    """
    user = get_user_from_db(current_user)
    if user:
        return {"message": "Access granted"}
    # Если пользователь не найден, возвращаем ошибку
    return {"error": "User not found"}


@app.get("/profile")
async def get_profile(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if not session_token:
        response.status_code = 401
        return {"message": "Session expired"}
    try:
        data = token_serializer.loads(session_token, max_age=300)
    except BadSignature:
        response.status_code = 401
        return {"message": "Invalid session"}
    expire_time = datetime.now() - cookie_cache[data]["timestamp"]
    if expire_time >= timedelta(minutes=3):
        cookie_cache[data]["timestamp"] = datetime.now()
        confirmation_token = token_serializer.dumps(data)
        response.set_cookie(key="session_token", value=confirmation_token, max_age=300)
    return {"username": cookie_cache[data]["user"].username}


allowed_lang = ["ru", "en"]


@app.get("/headers")
async def get_headers(headers: Annotated[CommonHeaders, Header()]):
    return {"User-Agent": headers.user_agent, "Accept-Language": headers.accept_language}


@app.get("/info")
async def get_info(headers: Annotated[CommonHeaders, Header()], response: Response):
    response.headers["X-Server-Time"] = datetime.now().isoformat(timespec="seconds")
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        },
    }
