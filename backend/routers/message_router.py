from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from enums.user_roles import UserRoles
from schemas.message_creation_request import MessageCreationRequest
from models.user_model import User

from services.message_service import MessageService
from services.permissions_service import PermissionsService
from database.postgres_connection import get_postgres_db


message_router = APIRouter(tags=["Messages"])

permissions_service = PermissionsService()
message_service = MessageService()

@message_router.get("/", status_code=200)
async def read_messages(
    current_user: User = Depends(permissions_service.check_roles_token([UserRoles.ADMIN])),
    db: Session = Depends(get_postgres_db)
):
    return message_service.get_all_messages(db)

@message_router.get("/conversation/{conversation_id}", status_code=200)
async def get_messages_by_conversation(
    conversation_id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    return message_service.get_messages_by_conversation_id(conversation_id, current_user, db)

@message_router.post("/conversation/{conversation_id}", status_code=201)
async def create_message(
    conversation_id: int,
    request: MessageCreationRequest,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    return message_service.create_message(conversation_id, request.content, current_user, db)

@message_router.get("/{message_id}", status_code=200)
async def get_message_by_id(
    message_id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    return message_service.get_message_by_id(message_id, current_user, db)

@message_router.delete("/{message_id}", status_code=200)
async def delete_message(
    message_id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    return message_service.delete_message(message_id, current_user, db)

@message_router.delete("/{message_id}/from-here", status_code=200)
async def delete_messages_from(
    message_id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    deleted = message_service.delete_messages_from(message_id, current_user, db)
    return {"deleted": deleted}
