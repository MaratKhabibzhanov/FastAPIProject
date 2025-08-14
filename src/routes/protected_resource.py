from fastapi import APIRouter, Depends, Request

from src.db.database import resources
from src.limiter.rate_limiter import RateByRoleLimiter
from src.models.models import Content, RoleEnum, UserInDB
from src.security.olac import OwnershipChecker
from src.security.rbac import PermissionChecker


protected_resource = APIRouter()
role_limiter = RateByRoleLimiter()


@protected_resource.get("/protected_resource/{username}")
@PermissionChecker(RoleEnum.GUEST)
# @limiter.limit(role_limiter.get_rate_limit_by_role)
@OwnershipChecker()
async def get_protected_resource(
    username: str, request: Request, current_user: UserInDB = Depends(role_limiter.get_full_user_info)
):
    return {"message": resources[username]["content"]}


@protected_resource.post("/protected_resource/{username}")
@PermissionChecker(RoleEnum.USER)
# @limiter.limit(role_limiter.get_rate_limit_by_role)
@OwnershipChecker()
async def post_protected_resource(
    username: str, request: Request, data: Content, current_user: UserInDB = Depends(role_limiter.get_full_user_info)
):
    resources[username] = {"content": data.content, "is_public": data.is_public}
    return {"message": f"New content - {resources[username]['content']}!"}


@protected_resource.put("/protected_resource/{username}")
@PermissionChecker(RoleEnum.USER)
# @limiter.limit(role_limiter.get_rate_limit_by_role)
@OwnershipChecker()
async def put_protected_resource(
    username: str, request: Request, data: Content, current_user: UserInDB = Depends(role_limiter.get_full_user_info)
):
    resources[username]["content"] = data.content
    return {"message": f"Edited content - {resources[username]['content']}!"}


@protected_resource.delete("/protected_resource/{username}")
@PermissionChecker(RoleEnum.USER)
# @limiter.limit(role_limiter.get_rate_limit_by_role)
@OwnershipChecker()
async def delete_protected_resource(
    username: str, request: Request, current_user: UserInDB = Depends(role_limiter.get_full_user_info)
):
    del resources[username]
    return {"message": "Content deleted!"}
