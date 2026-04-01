from pydantic import BaseModel, EmailStr
from typing import Optional


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None