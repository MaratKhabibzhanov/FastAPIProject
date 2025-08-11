import datetime
from typing import Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "090f461de41e4d7fd03be814a953a1438c305ab952a8a45c36f0f348527d1db5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def create_jwt_token(data: Dict):
    """
    Функция для создания JWT токена. Мы копируем входные данные, добавляем время истечения и кодируем токен.
    """
    to_encode = data.copy()
    expire = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Функция для получения пользователя из токена
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    """
    Функция для извлечения информации о пользователе из токена. Проверяем токен и извлекаем утверждение о пользователе.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен просрочен", headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не валидный токен", headers={"WWW-Authenticate": "Bearer"}
        )
