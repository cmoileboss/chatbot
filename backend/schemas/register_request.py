from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    '''Requête d'inscription'''

    username: str = Field(max_length=50, example="username")
    email: EmailStr = Field(max_length=150, example="user@example.com")
    password: str = Field(min_length=8, max_length=128, example="strongpassword123")