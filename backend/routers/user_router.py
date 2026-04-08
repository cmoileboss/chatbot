from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from enums.user_roles import UserRoles
from models.user_model import User
from schemas.user_response import user_response
from schemas.user_update_request import UserUpdateRequest
from services.user_service import UserService
from services.permissions_service import PermissionsService
from database.postgres_connection import get_postgres_db


user_router = APIRouter(tags=["Users"])

permissions_service = PermissionsService()
user_service = UserService()


@user_router.get("/", status_code=200, response_model=list[user_response])
async def read_all_users(
    current_user: User = Depends(permissions_service.check_roles_token([UserRoles.ADMIN])),
    db: Session = Depends(get_postgres_db),
):
    return user_service.get_all_users(db)


@user_router.get("/{id}", status_code=200, response_model=user_response)
async def read_user(
    id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db),
):
    return user_service.get_user_by_id(id, current_user, db)


@user_router.patch("/{id}", status_code=200, response_model=user_response)
async def update_user(
    id: int,
    request: UserUpdateRequest,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db),
):
    return user_service.update_user(id, request, current_user, db)


@user_router.delete("/{id}", status_code=204)
async def delete_user(
    id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db),
):
    user_service.delete_user(id, current_user, db)