from sqlalchemy.orm import Session

from repositories.conversation_repository import ConversationRepository
from models.conversation_model import Conversation
from models.user_model import User

from enums.user_roles import UserRoles

from fastapi import HTTPException


class ConversationService:
    '''Service de gestion des conversations'''

    def __init__(self):
        self.conversation_repository = ConversationRepository()

    def get_all_conversations(self, db: Session) -> list[Conversation]:
        '''Get all conversations.'''
        return self.conversation_repository.get_all_conversations(db)

    def create_conversation(self, user_id: int, title: str, current_user: User, db: Session) -> Conversation:
        '''Create a new conversation.'''
        if current_user.role != UserRoles.ADMIN and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas la permission de créer une conversation pour cet utilisateur.")
        if self.conversation_repository.exists_conversation_with_title_and_user_id(title, user_id, db):
            raise HTTPException(status_code=400, detail="Une conversation avec ce titre existe déjà pour cet utilisateur.")
        conversation = Conversation(user_id=user_id, title=title)
        return self.conversation_repository.create_conversation(conversation, db)

    def get_conversations_for_user(self, user_id: int, current_user: User, db: Session) -> list[Conversation]:
        '''Get all conversations for a specific user.'''
        if current_user.role != UserRoles.ADMIN and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas la permission d'accéder aux conversations de cet utilisateur.")
        return self.conversation_repository.get_conversations_by_user_id(user_id, db)

    def get_conversation_by_id(self, conversation_id: int, current_user: User, db: Session) -> Conversation:
        '''Get a conversation by its ID.'''
        conversation = self.conversation_repository.get_conversation_by_id(conversation_id, db)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")
        if current_user.role != UserRoles.ADMIN and current_user.id != conversation.user_id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas la permission d'accéder à cette conversation.")
        return conversation

    def update_conversation(self, conversation_id: int, title: str, current_user: User, db: Session) -> Conversation:
        '''Update an existing conversation.'''
        conversation = self.conversation_repository.get_conversation_by_id(conversation_id, db)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")
        if current_user.role != UserRoles.ADMIN and current_user.id != conversation.user_id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas la permission de modifier cette conversation.")
        if self.conversation_repository.exists_conversation_with_title_and_user_id(title, conversation.user_id, db):
            raise HTTPException(status_code=400, detail="Une conversation avec ce titre existe déjà pour cet utilisateur.")
        conversation.title = title
        return self.conversation_repository.update_conversation(conversation, db)

    def delete_conversation(self, conversation_id: int, current_user: User, db: Session) -> bool:
        '''Delete a conversation by its ID.'''
        conversation = self.conversation_repository.get_conversation_by_id(conversation_id, db)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")
        if current_user.role != UserRoles.ADMIN and current_user.id != conversation.user_id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas la permission de supprimer cette conversation.")
        return self.conversation_repository.delete_conversation(conversation_id, db)
    
    def get_conversation_history(self, conversation_id: int, current_user: User, db: Session) -> list[dict]:
        '''Get the conversation history as a list of {"role": "user"|"assistant", "content": str}'''
        conversation = self.get_conversation_by_id(conversation_id, current_user, db)
        return [
            {"role": message.role.value, "content": message.content}
            for message in conversation.messages
        ]