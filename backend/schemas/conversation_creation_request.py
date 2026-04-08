from pydantic import BaseModel, Field

class ConversationCreationRequest(BaseModel):
    '''Schéma pour la création d'une conversation.'''
    title: str = Field(max_length=100, json_schema_extra={"example": "Ma nouvelle conversation"})