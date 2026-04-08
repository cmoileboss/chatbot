import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from enums.user_roles import UserRoles
from models.user_model import User
from schemas.register_request import RegisterRequest
from services.auth_service import AuthService


def make_user(id: int, username: str, email: str, role: UserRoles) -> User:
    user = MagicMock(spec=User)
    user.id = id
    user.username = username
    user.email = email
    user.role = role
    return user


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def auth_service():
    service = AuthService()
    service.user_repository = MagicMock()
    return service


@pytest.fixture
def existing_user():
    user = make_user(1, "alice", "alice@example.com", UserRoles.USER)
    user.check_password = MagicMock(return_value=True)
    return user


# --- authenticate ---

class TestAuthenticate:
    def test_returns_user_on_valid_credentials(self, auth_service, db, existing_user):
        auth_service.user_repository.get_user_by_email.return_value = existing_user

        result = auth_service.authenticate("alice@example.com", "correct_password", db)

        assert result == existing_user

    def test_raises_401_if_user_not_found(self, auth_service, db):
        auth_service.user_repository.get_user_by_email.return_value = None

        with pytest.raises(HTTPException) as exc:
            auth_service.authenticate("unknown@example.com", "password", db)

        assert exc.value.status_code == 401

    def test_raises_401_on_wrong_password(self, auth_service, db, existing_user):
        existing_user.check_password.return_value = False
        auth_service.user_repository.get_user_by_email.return_value = existing_user

        with pytest.raises(HTTPException) as exc:
            auth_service.authenticate("alice@example.com", "wrong_password", db)

        assert exc.value.status_code == 401


# --- create_user ---

class TestCreateUser:
    def _make_request(self, username="newuser", email="new@example.com", password="strongpass1"):
        req = MagicMock(spec=RegisterRequest)
        req.username = username
        req.email = email
        req.password = password
        return req

    def test_creates_user_successfully(self, auth_service, db):
        auth_service.user_repository.is_email_taken.return_value = False
        auth_service.user_repository.is_username_taken.return_value = False
        auth_service.user_repository.create_user.return_value = None

        request = self._make_request()
        result = auth_service.create_user(request, db)

        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.role == UserRoles.USER
        auth_service.user_repository.create_user.assert_called_once()

    def test_raises_400_if_email_taken(self, auth_service, db):
        auth_service.user_repository.is_email_taken.return_value = True

        with pytest.raises(HTTPException) as exc:
            auth_service.create_user(self._make_request(), db)

        assert exc.value.status_code == 400

    def test_raises_400_if_username_taken(self, auth_service, db):
        auth_service.user_repository.is_email_taken.return_value = False
        auth_service.user_repository.is_username_taken.return_value = True

        with pytest.raises(HTTPException) as exc:
            auth_service.create_user(self._make_request(), db)

        assert exc.value.status_code == 400
