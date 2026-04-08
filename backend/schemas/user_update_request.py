from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserUpdateRequest(BaseModel):
    '''Schéma pour la mise à jour d'un utilisateur'''
    username: Optional[str] = Field(default=None, max_length=50, json_schema_extra={"example": "username"})
    email: Optional[EmailStr] = Field(default=None, max_length=150, json_schema_extra={"example": "user@example.com"})
    password: Optional[str] = Field(default=None, min_length=8, max_length=128, json_schema_extra={"example": "strongpassword123"})