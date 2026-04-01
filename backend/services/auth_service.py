import bcrypt
from fastapi import HTTPException

from enums.user_roles import UserRoles
from database.postgres_connection import get_postgres_db
from schemas.register_request import RegisterRequest
from repositories.user_repository import UserRepository
from models.user_model import User


class AuthService:
    '''Service de gestion de l'authentification des utilisateurs'''

    def __init__(self):
        self.user_repository = UserRepository()

    def authenticate(self, email: str, password: str, db) -> User:
        '''Authenticate a user by their email and password.
        Args:
            email (str): The email of the user.
            password (str): The plaintext password to verify.
            db: SQLAlchemy Session
        Returns:
            User: The authenticated user object if credentials are valid.
        '''
        user = self.user_repository.get_user_by_email(email, db)
        if user is None:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        if user.check_password(password):
            return user
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    def create_user(self, register_request: RegisterRequest, db) -> User:
        '''Create a new user with the given information.
        Args:
            username (str): The username of the new user.
            email (str): The email of the new user.
            password (str): The plaintext password for the new user.
            role (str): The role of the new user (e.g., 'admin', 'user').
            db: SQLAlchemy Session
        Returns:
            User: The created user object.
        '''
        if self.user_repository.is_email_taken(register_request.email, db):
            raise HTTPException(status_code=400, detail="Email déjà utilisé")

        if self.user_repository.is_username_taken(register_request.username, db):
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

        user = User(username=register_request.username, email=register_request.email, password=register_request.password, role=UserRoles.USER)
        self.user_repository.create_user(user, db)
        return user