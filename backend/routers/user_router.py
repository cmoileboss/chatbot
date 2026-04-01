from fastapi import APIRouter, Depends

from enums.user_roles import UserRoles
from schemas.user_response import user_response
from services.user_service import UserService
from services.permissions_service import PermissionsService
from database.postgres_connection import get_postgres_db


user_router = APIRouter(tags=["Users"])

permissions_service = PermissionsService()
user_service = UserService()


@user_router.get("/{id}", status_code=200, response_model=user_response)
async def read_user(
    id: int,
    user=Depends(permissions_service.check_roles_token([UserRoles.ADMIN, UserRoles.USER])),
    db=Depends(get_postgres_db),
):
    '''Endpoint pour récupérer les informations d'un utilisateur par son id (protégé).
    Args:
        id (int): L'identifiant de l'utilisateur.
    Returns:
        user_response: Un dictionnaire contenant les informations de l'utilisateur.
    '''
    return user_service.get_user_by_id(id, user, db)

