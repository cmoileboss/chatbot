from fastapi import HTTPException

from sqlalchemy.orm import Session

from enums.user_roles import UserRoles
from models.user_model import User
from repositories.user_repository import UserRepository


class UserService:
    '''Service de gestion des utilisateurs'''
    
    def __init__(self):
        self.user_repository = UserRepository()

    def get_all_users(self, db: Session):
        '''Get all users from the database
        Args:
            db: SQLAlchemy Session
        Returns:
            List[User]: A list of all user objects in the database'''
        return self.user_repository.get_all_users(db)

    def get_user_by_id(self, user_id: int, current_user: User, db: Session):
        '''Get a user by ID, checking that the current user is authorized to access it.
        Args:
            user_id (int): The ID of the user to retrieve.
            current_user (User): The currently authenticated user.
            db: SQLAlchemy Session
        Returns:
            User: The user object if found and authorized.
        Raises:
            HTTPException 404: If the user is not found.
            HTTPException 403: If the current user is not allowed to access this resource.
        '''
        user = self.user_repository.get_user_by_id(user_id, db)
        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        if current_user.role != UserRoles.ADMIN and user.id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès interdit")
        return user
    
    def get_user_by_email(self, email: str, current_user: User, db: Session):
        '''Get a user by email.
        Args:
            email (str): The email of the user to retrieve.
            current_user (User): The currently authenticated user.
            db: SQLAlchemy Session
        Returns:
            User: The user object if found, otherwise None.
        Raises:
            HTTPException 404: If the user is not found.
            HTTPException 403: If the current user is not allowed to access this resource.'''
        if current_user.role != UserRoles.ADMIN and email != current_user.email:
            raise HTTPException(status_code=403, detail="Accès interdit")
        
        user = self.user_repository.get_user_by_email(email, db)
        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return user

    def get_user_by_username(self, username: str, current_user: User, db: Session):
        '''Get a user by username.
        Args:
            username (str): The username of the user to retrieve.
            current_user (User): The currently authenticated user.
            db: SQLAlchemy Session
        Returns:
            User: The user object if found, otherwise None.
        Raises:
            HTTPException 404: If the user is not found.
            HTTPException 403: If the current user is not allowed to access this resource.'''
        if current_user.role != UserRoles.ADMIN and username != current_user.username:
            raise HTTPException(status_code=403, detail="Accès interdit")
        
        user = self.user_repository.get_user_by_username(username, db)
        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return user
    
    def update_user(self, user_to_update: UserUpdateRequest, current_user: User, db: Session):
        '''Update a user's information.
        Args:
            user_to_update (UserUpdateRequest): The updated user information.
            current_user (User): The currently authenticated user.
            db: SQLAlchemy Session
        Returns:
            User: The updated user object.
        Raises:
            HTTPException 404: If the user is not found.
            HTTPException 403: If the current user is not allowed to update this user.'''
        if current_user.role != UserRoles.ADMIN and user_to_update.id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès interdit")
        
        user = self.user_repository.get_user_by_id(user_to_update.id, db)
        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        user.username = user_to_update.username or user.username
        user.email = user_to_update.email or user.email
        if user_to_update.password_hash:
            user.set_password(user_to_update.password_hash)

        return self.user_repository.update_user(user, db)
    
    def delete_user(self, id: int, current_user: User, db: Session):
        '''Delete a user by ID.
        Args:
            id (int): The ID of the user to delete.
            current_user (User): The currently authenticated user.
            db: SQLAlchemy Session
        Returns:
            None
        Raises:
            HTTPException 404: If the user is not found.
            HTTPException 403: If the current user is not allowed to delete this user.'''
        if current_user.role != UserRoles.ADMIN and id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès interdit")
        
        user = self.user_repository.get_user_by_id(id, db)
        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        self.user_repository.delete_user(user, db)