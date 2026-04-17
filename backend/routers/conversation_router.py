
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from enums.user_roles import UserRoles
from schemas.conversation_creation_request import ConversationCreationRequest
from models.user_model import User

from services.conversation_service import ConversationService
from services.permissions_service import PermissionsService
from database.postgres_connection import get_postgres_db


conversation_router = APIRouter(tags=["Conversations"])

permissions_service = PermissionsService()
conversation_service = ConversationService()

@conversation_router.get("/", status_code=200)
async def read_conversations(
    current_user: User = Depends(permissions_service.check_roles_token([UserRoles.ADMIN])),
    db: Session = Depends(get_postgres_db)
):
    return conversation_service.get_all_conversations(db)

@conversation_router.post("/", status_code=201)
async def create_conversation(
    request: ConversationCreationRequest,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    return conversation_service.create_conversation(current_user.id, request.title, current_user, db)

@conversation_router.get("/user/{user_id}", status_code=200)
async def get_conversations_for_user(
    user_id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    if user_id == -1:
        return None
    return conversation_service.get_conversations_for_user(user_id, current_user, db)

@conversation_router.get("/{conversation_id}", status_code=200)
async def get_conversation_by_id(
    conversation_id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    return conversation_service.get_conversation_by_id(conversation_id, current_user, db)

@conversation_router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    conversation_service.delete_conversation(conversation_id, current_user, db)

@conversation_router.patch("/{conversation_id}", status_code=200)
async def rename_conversation(
    conversation_id: int,
    request: ConversationCreationRequest,
    current_user: User = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    return conversation_service.update_conversation(conversation_id, request.title, current_user, db)