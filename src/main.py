from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, Header, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from itsdangerous import BadSignature, URLSafeTimedSerializer

from src.models.models import cookie_cache
from src.schemas import CommonHeaders, User

from .app import app
from .config import load_config as config
from .security import create_jwt_token, get_user_from_token
from .utils import authenticate_user, create_new_user, get_user_from_db


token_serializer = URLSafeTimedSerializer(secret_key=config().secret_key)


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = User(username=form_data.username, password=form_data.password)
    authenticated_user = authenticate_user(user)
    token = create_jwt_token({"sub": authenticated_user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/register")
def register(user: User):
    create_new_user(user)
    return {"message": f"Welcome, {user.username}!"}


@app.get("/protected_resource")
def protected_resource(current_user: str = Depends(get_user_from_token)):
    """
    Этот маршрут защищен и требует токен. Если токен действителен, мы возвращаем информацию о пользователе.
    """
    user = get_user_from_db(current_user)
    if user:
        return {"username": user.username}
    # Если пользователь не найден, возвращаем ошибку
    return {"error": "User not found"}


@app.get("/profile")
def get_profile(request: Request, response: Response):
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
