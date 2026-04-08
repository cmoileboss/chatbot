from sqlalchemy.orm import Session

from models.message_model import Message


class MessageRepository:
    '''Repository for managing messages in the database.'''

    def create_message(self, message: Message, db: Session) -> Message:
        '''Create a new message in a conversation.'''
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_message_by_id(self, message_id: int, db: Session) -> Message | None:
        '''Get a message by its ID.'''
        return db.query(Message).filter(Message.id == message_id).first()

    def get_messages_by_conversation_id(self, conversation_id: int, db: Session) -> list[Message]:
        '''Get all messages for a specific conversation.'''
        return db.query(Message).filter(Message.conversation_id == conversation_id).all()

    def delete_message(self, message_id: int, db: Session) -> bool:
        '''Delete a message by its ID.'''
        message = db.query(Message).filter(Message.id == message_id).first()
        if message:
            db.delete(message)
            db.commit()
            return True
        return False