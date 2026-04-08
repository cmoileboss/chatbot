from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from enums.user_roles import UserRoles
from models.user_model import User
from schemas.metadata_request import MetadataCreationRequest, MetadataUpdateRequest
from services.metadata_service import MetadataService
from services.permissions_service import PermissionsService
from database.postgres_connection import get_postgres_db


metadata_router = APIRouter(tags=["Metadata"])

permissions_service = PermissionsService()
metadata_service = MetadataService()


@metadata_router.get("/", status_code=200)
async def get_all_metadata(
    current_user: User = Depends(permissions_service.check_roles_token([UserRoles.ADMIN])),
    db: Session = Depends(get_postgres_db)
):
    return metadata_service.get_all(db)


@metadata_router.get("/{metadata_id}", status_code=200)
async def get_metadata_by_id(
    metadata_id: int,
    current_user: User = Depends(permissions_service.check_roles_token([UserRoles.ADMIN])),
    db: Session = Depends(get_postgres_db)
):
    return metadata_service.get_by_id(metadata_id, db)


@metadata_router.post("/", status_code=201)
async def create_metadata(
    request: MetadataCreationRequest,
    current_user: User = Depends(permissions_service.check_roles_token([UserRoles.ADMIN])),
    db: Session = Depends(get_postgres_db)
):
    return metadata_service.create(request, db)


@metadata_router.patch("/{metadata_id}", status_code=200)
async def update_metadata(
    metadata_id: int,
    request: MetadataUpdateRequest,
    current_user: User = Depends(permissions_service.check_roles_token([UserRoles.ADMIN])),
    db: Session = Depends(get_postgres_db)
):
    return metadata_service.update(metadata_id, request, db)


@metadata_router.delete("/{metadata_id}", status_code=200)
async def delete_metadata(
    metadata_id: int,
    current_user: User = Depends(permissions_service.check_roles_token([UserRoles.ADMIN])),
    db: Session = Depends(get_postgres_db)
):
    return metadata_service.delete(metadata_id, db)
