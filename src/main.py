from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Header, Request, Response
from itsdangerous import BadSignature, URLSafeTimedSerializer

from src.models.models import Credentials, admin_user, cookie_cache
from src.schemas import CommonHeaders

from .config import load_config as config


app = FastAPI()

feedbacks = list()

token_serializer = URLSafeTimedSerializer(secret_key=config().secret_key)


@app.post("/login")
def login(user: Credentials, response: Response):
    if user == admin_user:
        user_id = str(uuid4())
        cookie_cache[user_id] = dict(user=user, timestamp=datetime.now())
        confirmation_token = token_serializer.dumps(user_id)
        response.set_cookie(key="session_token", value=confirmation_token, max_age=300, httponly=True)
        return {"message": "Cookie has been set!"}
    return {"message": "Invalid credentials!"}


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
