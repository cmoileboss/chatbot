from sqlalchemy.orm import Session

from fastapi import HTTPException

from enums.sender_role import SenderRole
from enums.user_roles import UserRoles
from models.message_model import Message
from models.user_model import User
from repositories.conversation_repository import ConversationRepository
from repositories.message_repository import MessageRepository


class MessageService:
    '''Service de gestion des messages'''

    def __init__(self):
        self.message_repository = MessageRepository()
        self.conversation_repository = ConversationRepository()

    def _check_conversation_access(self, conversation_id: int, current_user: User, db: Session):
        '''Vérifie que la conversation existe et que l'utilisateur y a accès.'''
        conversation = self.conversation_repository.get_conversation_by_id(conversation_id, db)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation non trouvée")
        if current_user.role != UserRoles.ADMIN and current_user.id != conversation.user_id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas la permission d'accéder à cette conversation.")
        return conversation

    def get_all_messages(self, db: Session) -> list[Message]:
        '''Get all messages.'''
        return self.message_repository.get_all_messages(db)

    def get_messages_by_conversation_id(self, conversation_id: int, current_user: User, db: Session) -> list[Message]:
        '''Get all messages for a specific conversation.'''
        self._check_conversation_access(conversation_id, current_user, db)
        return self.message_repository.get_messages_by_conversation_id(conversation_id, db)

    def create_message(self, conversation_id: int, role: SenderRole, content: str, current_user: User, db: Session) -> Message:
        '''Create a new message in a conversation.'''
        self._check_conversation_access(conversation_id, current_user, db)
        message = Message(conversation_id=conversation_id, role=role, content=content)
        return self.message_repository.create_message(message, db)

    def get_message_by_id(self, message_id: int, current_user: User, db: Session) -> Message:
        '''Get a message by its ID.'''
        message = self.message_repository.get_message_by_id(message_id, db)
        if message is None:
            raise HTTPException(status_code=404, detail="Message non trouvé")
        self._check_conversation_access(message.conversation_id, current_user, db)
        return message

    def delete_message(self, message_id: int, current_user: User, db: Session) -> bool:
        '''Delete a message by its ID.'''
        message = self.message_repository.get_message_by_id(message_id, db)
        if message is None:
            raise HTTPException(status_code=404, detail="Message non trouvé")
        self._check_conversation_access(message.conversation_id, current_user, db)
        return self.message_repository.delete_message(message_id, db)

    def delete_messages_from(self, message_id: int, current_user: User, db: Session) -> int:
        '''Delete a message and all subsequent messages in the same conversation.'''
        message = self.message_repository.get_message_by_id(message_id, db)
        if message is None:
            raise HTTPException(status_code=404, detail="Message non trouvé")
        self._check_conversation_access(message.conversation_id, current_user, db)
        return self.message_repository.delete_messages_from(message_id, message.conversation_id, db)