from pydantic import BaseModel, Field

class MessageCreationRequest(BaseModel):
    '''Schéma pour la création d'un message.'''
    content: str = Field(max_length=1000, json_schema_extra={"example": "Bonjour, comment ça va?"})
