from fastapi import Depends
from sqlalchemy.orm import Session

from database.postgres_connection import get_postgres_db
from models.user_model import User


class UserRepository:
    '''Repository for managing user data in the database'''

    def is_email_taken(self, email: str, db: Session) -> bool:
        '''Check if an email is already taken by another user
        Args:
            email (str): The email to check.
        Returns:
            bool: True if the email is already taken, False otherwise.'''
        return db.query(User).filter(User.email == email).first() is not None

    def is_username_taken(self, username: str, db: Session) -> bool:
        '''Check if a username is already taken by another user
        Args:
            username (str): The username to check.
        Returns:
            bool: True if the username is already taken, False otherwise.'''
        return db.query(User).filter(User.username == username).first() is not None

    def get_all_users(self, db: Session):
        '''Get all users
        Returns:
            List[User]: A list of all user objects in the database'''
        return db.query(User).all()

    def get_user_by_id(self, user_id: int, db: Session):
        '''Get a user by their ID
        Args:
            user_id (int): The ID of the user to retrieve.
        Returns:
            User: The user object if found, else None.'''
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str, db: Session):
        '''Get a user by their username
        Args:
            username (str): The username of the user to retrieve.
        Returns:
            User: The user object if found, else None.'''
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str, db: Session):
        '''Get a user by their email address
        Args:
            email (str): The email of the user to retrieve.
        Returns:
            User: The user object if found, else None.'''
        return db.query(User).filter(User.email == email).first()

    def create_user(self, new_user: User, db: Session):
        '''Create a new user
        Args:
            new_user (User): The user object to create.
        Returns:
            User: The created user object.'''
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    def update_user(self, user: User, db: Session):
        '''Update an existing user
        Args:
            user (User): The user object to update.
        Returns:
            User: The updated user object.'''
        db.commit()
        db.refresh(user)
        return user
    
    def delete_user(self, user: User, db: Session):
        '''Delete a user
        Args:
            user (User): The user object to delete.'''
        db.delete(user)
        db.commit()