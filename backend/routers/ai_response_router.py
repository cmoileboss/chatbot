from fastapi import APIRouter, Depends, UploadFile, File
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
from services.rag_service import RagService, SUPPORTED_EXTENSIONS

from schemas.prompt_request import PromptRequest

import os
import tempfile


ai_response_router = APIRouter(tags=["AI Response"])

local_ai_service = LocalAiService(ai_model="llama3.2")
permissions_service = PermissionsService()
conversation_service = ConversationService()
message_service = MessageService()
rag_service = RagService()

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


@ai_response_router.post("/upload", status_code=200)
async def upload_document(
    file: UploadFile = File(...),
    current_user = Depends(permissions_service.get_current_user)
):
    '''Upload and index a document for RAG.'''
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ''
    if ext not in SUPPORTED_EXTENSIONS:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Format non supporté. Formats acceptés : {', '.join(SUPPORTED_EXTENSIONS)}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        count = rag_service.ingest_file(tmp_path, original_filename=file.filename, collection=str(current_user.id))
    finally:
        os.unlink(tmp_path)
    return {"filename": file.filename, "chunks_indexed": count}


@ai_response_router.get("/documents", status_code=200)
async def list_documents(current_user = Depends(permissions_service.get_current_user)):
    '''Retourne la liste des documents indexés dans le RAG de l\'utilisateur courant.'''
    return rag_service.list_documents(str(current_user.id))


@ai_response_router.delete("/documents", status_code=200)
async def reset_documents(current_user = Depends(permissions_service.get_current_user)):
    '''Supprime tous les documents RAG indexés pour l\'utilisateur courant.'''
    rag_service.reset_collection(str(current_user.id))
    return {"message": "Documents supprimés avec succès."}


@ai_response_router.delete("/documents/{filename:path}", status_code=200)
async def delete_document(
    filename: str,
    current_user = Depends(permissions_service.get_current_user)
):
    '''Supprime un document spécifique du RAG (tous ses chunks).'''
    deleted = rag_service.delete_document(filename, str(current_user.id))
    return {"filename": filename, "chunks_deleted": deleted}


@ai_response_router.post("/chat-rag/{conversation_id}", status_code=200, response_class=PlainTextResponse)
async def generate_rag_response(
    conversation_id: int,
    request: PromptRequest,
    current_user = Depends(permissions_service.get_current_user),
    db: Session = Depends(get_postgres_db)
):
    '''Chat with RAG context injected from the user's indexed documents.'''
    message_service.create_message(conversation_id, SenderRole.USER, request.prompt, current_user, db)
    context = rag_service.retrieve_context(request.prompt, collection=str(current_user.id))
    history = conversation_service.get_conversation_history(conversation_id, current_user, db)
    if context:
        ai_response = local_ai_service.converse_with_context(history, context)
    else:
        ai_response = local_ai_service.converse_llm(history)
    message_service.create_message(conversation_id, SenderRole.ASSISTANT, ai_response, current_user, db)
    return ai_response


@ai_response_router.get("/models", status_code=200)
async def list_models(current_user = Depends(permissions_service.get_current_user)):
    '''Return the list of models available in Ollama and the currently active model.'''
    return {
        "current": local_ai_service.get_model(),
        "available": local_ai_service.list_models(),
    }


@ai_response_router.put("/model", status_code=200)
async def set_model(
    body: dict,
    current_user = Depends(permissions_service.get_current_user)
):
    '''Change the active AI model.'''
    model = body.get("model", "").strip()
    if not model:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Le champ 'model' est requis.")
    local_ai_service.set_model(model)
    return {"model": local_ai_service.get_model()}


@ai_response_router.post("/models/pull")
async def pull_model(
    body: dict,
    current_user = Depends(permissions_service.get_current_user)
):
    '''Stream la progression du téléchargement d\'un modèle Ollama (NDJSON).'''
    from fastapi import HTTPException
    from fastapi.responses import StreamingResponse
    model = body.get("model", "").strip()
    if not model:
        raise HTTPException(status_code=400, detail="Le champ 'model' est requis.")
    return StreamingResponse(
        local_ai_service.pull_model_stream(model),
        media_type="application/x-ndjson",
    )