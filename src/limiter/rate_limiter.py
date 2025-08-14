from fastapi import Depends, HTTPException, status

from src.models.models import RoleEnum, UserInDB
from src.security.security import get_user_from_token


class RateByRoleLimiter:
    RATE_BY_ROLE = {RoleEnum.ADMIN: "10/minute", RoleEnum.USER: "5/minute", RoleEnum.GUEST: "1/minute"}

    def __init__(self):
        self.role = None

    def get_full_user_info(self, user: UserInDB = Depends(get_user_from_token)):
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.role = user.role
        return user

    def get_rate_limit_by_role(self):
        return self.RATE_BY_ROLE[self.role]
