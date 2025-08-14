from functools import wraps

from fastapi import HTTPException, status

from src.db.database import RoleEnum


class PermissionChecker:
    """Декоратор для проверки ролей пользователя"""

    def __init__(self, role: str):
        self.role = role

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")  # Получаем текущего пользователя
            if not user:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется аутентификация")

            if (
                user.role == RoleEnum.ADMIN
                or user.role == RoleEnum.USER
                and self.role in (RoleEnum.USER, RoleEnum.GUEST)
            ):
                return await func(*args, **kwargs)

            if user.role != self.role:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для доступа")
            return await func(*args, **kwargs)

        return wrapper
