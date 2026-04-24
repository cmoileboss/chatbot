from fastapi import APIRouter, Depends
from fastapi.params import Depends
from fastapi.responses import PlainTextResponse

from sqlalchemy.orm import Session

from services.permissions_service import PermissionsService
from database.postgres_connection import get_postgres_db

from enums.sender_role import SenderRole

from services.message_service import MessageService
from services.conversation_service import ConversationService
from services.auth_service import AuthService
from services.local_ai_service import LocalAiService

from schemas.prompt_request import PromptRequest


ai_response_router = APIRouter(tags=["AI Response"])

local_ai_service = LocalAiService(ai_model="llama3.2")
permissions_service = PermissionsService()
conversation_service = ConversationService()
message_service = MessageService()

@ai_response_router.post("/generate", status_code=200, response_class=PlainTextResponse)
async def generate_response(request: PromptRequest):
    '''Endpoint to generate a response from the local AI language model based on a prompt.'''
    return local_ai_service.response_llm(request.prompt)


@ai_response_router.post("/chat/{conversation_id}", status_code=200, response_class=PlainTextResponse)
async def generate_chat_response(conversation_id: int, request: PromptRequest, current_user = Depends(permissions_service.get_current_user), db: Session = Depends(get_postgres_db)):
    '''Endpoint to generate a response from the local AI language model based on conversation history.
    Args:
        conversation_id: The ID of the conversation.
        request: The request body containing the prompt for the AI model.
    '''
    message_service.create_message(conversation_id, SenderRole.USER, request.prompt, current_user, db)
    history = conversation_service.get_conversation_history(conversation_id, current_user, db)
    ai_response = local_ai_service.converse_llm(history)
    message_service.create_message(conversation_id, SenderRole.ASSISTANT, ai_response, current_user, db)
    return ai_response