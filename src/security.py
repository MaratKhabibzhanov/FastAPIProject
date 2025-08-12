import datetime
from typing import Dict, Tuple

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from .config import load_config as config
from .exceptions import ExpireTokenException, InvalidTokenException
from .models.models import refresh_tokens


conf = config()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", refreshUrl="refresh")


def create_jwt_tokens(data: Dict) -> Tuple[str, str]:
    """
    Функция для создания JWT токена. Мы копируем входные данные, добавляем время истечения и кодируем токен.
    """
    to_access = data.copy()
    to_refresh = data.copy()
    expire_access = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=conf.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_access.update({"exp": expire_access, "type": "access"})
    expire_refresh = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=conf.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_refresh.update({"exp": expire_refresh, "type": "refresh"})
    access_token = jwt.encode(to_access, conf.SECRET_KEY, algorithm=conf.ALGORITHM)
    refresh_token = jwt.encode(to_refresh, conf.SECRET_KEY, algorithm=conf.ALGORITHM)
    refresh_tokens[data["sub"]] = refresh_token
    return access_token, refresh_token


# Функция для получения пользователя из токена
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    """
    Функция для извлечения информации о пользователе из токена. Проверяем токен и извлекаем утверждение о пользователе.
    """
    try:
        payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[conf.ALGORITHM])
        if payload.get("type") != "access":
            raise InvalidTokenException()
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise ExpireTokenException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()


def update_refresh_token(token: str) -> Tuple[str, str]:
    try:
        payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[conf.ALGORITHM])
        username = payload.get("sub")
        if payload.get("type") != "refresh" or not refresh_tokens.get(username):
            raise InvalidTokenException()
        return create_jwt_tokens({"sub": username})
    except jwt.ExpiredSignatureError:
        raise ExpireTokenException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()
