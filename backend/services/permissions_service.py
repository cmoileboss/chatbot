from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie

from sqlalchemy.orm import Session

from jose import jwt, JWTError

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

from datetime import datetime, timedelta

from dotenv import load_dotenv
import jwt
import os

from enums.user_roles import UserRoles
from models.user_model import User
from repositories.user_repository import UserRepository

from database.postgres_connection import get_postgres_db


cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

class PermissionsService:
    '''Service de gestion des tokens d'authentification et des permissions'''
    
    def __init__(self):
        load_dotenv()
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.ALGORITHM = os.getenv('ALGORITHM', 'HS256')
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
        self.user_repository = UserRepository()


    def create_access_token(self, email: str) -> str:
        """Create a JWT access token for the given user email.
        Args:
            email (str): The email of the user.
        Returns:
            token (str): The encoded JWT token.
        """
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(email),
            "iat": datetime.now(tz=timezone.utc),
            "exp": expire
        }

        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)


    def verify_access_token(self, token: str) -> str:
        '''Verify the given JWT access token and return the email if valid.
        Args:
            token (str): The JWT token to verify.
        Returns:
            email (str): The email extracted from the token if valid.
        Raises:
            ValueError: If the token is invalid or expired.
        '''
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            email = payload.get("sub")
            if email is None:
                raise ValueError("Token invalide (sub manquant)")

            return email

        except JWTError:
            raise HTTPException(status_code=401, detail="Token invalide ou expiré")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Erreur lors de la vérification du token : {str(e)}")


    async def get_current_user(self, db: Session = Depends(get_postgres_db), access_token: str = Depends(cookie_scheme)) -> User:
        '''Get the current authenticated user based on the provided access token.
        Args:
            db (Session): The database session (injected via Depends).
            access_token (str): The JWT access token from the cookie (injected via Depends).
        Returns:
            User: The current authenticated user.
        Raises:
            HTTPException: If the user is not authenticated or not found.
        '''
        if access_token is None:
            raise HTTPException(status_code=401, detail="Non authentifié")

        try:
            email = self.verify_access_token(access_token)
            user = self.user_repository.get_user_by_email(email, db)
            if user is None:
                raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
            return user
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))


    def check_roles_token(self, roles: list[UserRoles]):
        '''Dependency to check if the current user has one of the specified roles.
        Args:
            roles (list[UserRoles]): A list of allowed user roles.
        Returns:
            User: The current authenticated user if they have one of the specified roles.
        Raises:
            HTTPException: If the user does not have the required role or is not authenticated.
        '''
        def role_checker(user = Depends(self.get_current_user)):
            if user.role not in roles:
                raise HTTPException(status_code=403, detail="Accès refusé")
            return user

        return role_checker