from sqlalchemy.orm import Session

from models.conversation_model import Conversation


class ConversationRepository:
    '''Repository for managing conversations in the database.'''

    def get_all_conversations(self, db: Session) -> list[Conversation]:
        '''Get all conversations.'''
        return db.query(Conversation).all()

    def create_conversation(self, conversation: Conversation, db: Session) -> Conversation:
        '''Create a new conversation.'''
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def get_conversation_by_id(self, conversation_id: int, db: Session) -> Conversation | None:
        '''Get a conversation by its ID.'''
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_conversations_by_user_id(self, user_id: int, db: Session) -> list[Conversation]:
        '''Get all conversations for a specific user.'''
        return db.query(Conversation).filter(Conversation.user_id == user_id).all()

    def get_conversation_by_title_and_user_id(self, title: str, user_id: int, db: Session) -> Conversation | None:
        '''Get a conversation by its title and user ID.'''
        return db.query(Conversation).filter(Conversation.title == title, Conversation.user_id == user_id).first()

    def exists_conversation_with_title_and_user_id(self, title: str, user_id: int, db: Session) -> bool:
        '''Check if a conversation with the given title and user ID already exists.'''
        return db.query(Conversation).filter(Conversation.title == title, Conversation.user_id == user_id).first() is not None

    def update_conversation(self, conversation: Conversation, db: Session) -> Conversation:
        '''Update an existing conversation.'''
        db.merge(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def delete_conversation(self, conversation_id: int, db: Session) -> bool:
        '''Delete a conversation by its ID.'''
        conversation = self.get_conversation_by_id(conversation_id, db)
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False