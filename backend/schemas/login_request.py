from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    '''Requête de connexion pour l'authentification'''

    email: EmailStr = Field(max_length=150, json_schema_extra={"example": "user@example.com"})
    password: str = Field(min_length=8, max_length=128, json_schema_extra={"example": "strongpassword123"})