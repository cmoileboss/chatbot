from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    '''Schema for the request body when sending a prompt to the AI model.'''
    prompt: str = Field(max_length=1000, json_schema_extra={"example": "Quelle est la capitale de la France ?"})