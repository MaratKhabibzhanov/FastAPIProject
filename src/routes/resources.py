from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from itsdangerous import BadSignature, URLSafeTimedSerializer

from src.config import load_config as config
from src.db.database import cookie_cache
from src.limiter.limiter import limiter
from src.limiter.rate_limiter import RateByRoleLimiter
from src.models.models import CommonHeaders, RoleEnum, UserInDB
from src.security.rbac import PermissionChecker


resource = APIRouter()
token_serializer = URLSafeTimedSerializer(secret_key=config().SECRET_KEY)
role_limiter = RateByRoleLimiter()


@resource.get("/admin_resource")
@PermissionChecker(RoleEnum.ADMIN)
@limiter.limit(role_limiter.get_rate_limit_by_role)
async def admin_resource(request: Request, current_user: UserInDB = Depends(role_limiter.get_full_user_info)):
    return {"message": f"Welcome {current_user.username}!"}


@resource.get("/user_resource")
@PermissionChecker(RoleEnum.USER)
@limiter.limit(role_limiter.get_rate_limit_by_role)
async def user_resource(request: Request, current_user: UserInDB = Depends(role_limiter.get_full_user_info)):
    return {"message": f"Welcome {current_user.username}!"}


@resource.get("/guest_resource")
@PermissionChecker(RoleEnum.GUEST)
@limiter.limit(role_limiter.get_rate_limit_by_role)
async def guest_resource(request: Request, current_user: UserInDB = Depends(role_limiter.get_full_user_info)):
    return {"message": f"Welcome {current_user.username}!"}


@resource.get("/profile")
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


@resource.get("/headers")
async def get_headers(headers: Annotated[CommonHeaders, Header()]):
    return {"User-Agent": headers.user_agent, "Accept-Language": headers.accept_language}


@resource.get("/info")
async def get_info(headers: Annotated[CommonHeaders, Header()], response: Response):
    response.headers["X-Server-Time"] = datetime.now().isoformat(timespec="seconds")
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        },
    }
