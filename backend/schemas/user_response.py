from pydantic import BaseModel, EmailStr, Field

from enums.user_roles import UserRoles


class user_response(BaseModel):
    '''Réponse contenant les informations d'un utilisateur'''

    id: int
    username: str
    email: EmailStr
    role: UserRoles