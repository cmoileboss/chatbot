from pydantic import BaseModel, Field

from enums.sender_role import SenderRole

class MessageCreationRequest(BaseModel):
    '''Schéma pour la création d'un message.'''
    role: SenderRole = Field(..., json_schema_extra={"example": "user, assistant, system"})
    content: str = Field(max_length=1000, json_schema_extra={"example": "Bonjour, comment ça va?"})
