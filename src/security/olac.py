from functools import wraps

from fastapi import HTTPException, Request, status

from src.db.database import RoleEnum, resources
from src.models.models import UserInDB


class OwnershipChecker:
    """Декоратор для проверки собственника объекта"""

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            user: UserInDB = kwargs.get("current_user")
            request_username: str = kwargs.get("username")
            if not user:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется аутентификация")

            if request.method != "POST" and not resources.get(request_username):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отсутствует запрашиваемый ресурс")

            if user.role == RoleEnum.ADMIN:
                return await func(*args, **kwargs)

            if request.method == "GET" and self._check_for_get(user, request_username):
                return await func(*args, **kwargs)

            if request.method in ("PUT", "POST", "DELETE") and user.username == request_username:
                return await func(*args, **kwargs)

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для доступа")
            # return await func(*args, **kwargs)

        return wrapper

    @staticmethod
    def _check_for_get(user: UserInDB, request_username: str) -> bool:
        return resources[request_username]["is_public"] or user.username == request_username
