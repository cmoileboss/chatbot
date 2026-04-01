import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from enums.user_roles import UserRoles
from models.user_model import User
from services.user_service import UserService


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
def user_service():
    service = UserService()
    service.user_repository = MagicMock()
    return service


@pytest.fixture
def admin_user():
    return make_user(1, "admin", "admin@example.com", UserRoles.ADMIN)


@pytest.fixture
def regular_user():
    return make_user(2, "user", "user@example.com", UserRoles.USER)


@pytest.fixture
def other_user():
    return make_user(3, "other", "other@example.com", UserRoles.USER)


# --- get_all_users ---

class TestGetAllUsers:
    def test_returns_all_users(self, user_service, db, admin_user, regular_user):
        user_service.user_repository.get_all_users.return_value = [admin_user, regular_user]

        result = user_service.get_all_users(db)

        assert result == [admin_user, regular_user]
        user_service.user_repository.get_all_users.assert_called_once_with(db)

    def test_returns_empty_list(self, user_service, db):
        user_service.user_repository.get_all_users.return_value = []

        result = user_service.get_all_users(db)

        assert result == []


# --- get_user_by_id ---

class TestGetUserById:
    def test_admin_can_access_any_user(self, user_service, db, admin_user, other_user):
        user_service.user_repository.get_user_by_id.return_value = other_user

        result = user_service.get_user_by_id(other_user.id, admin_user, db)

        assert result == other_user

    def test_user_can_access_own_profile(self, user_service, db, regular_user):
        user_service.user_repository.get_user_by_id.return_value = regular_user

        result = user_service.get_user_by_id(regular_user.id, regular_user, db)

        assert result == regular_user

    def test_user_cannot_access_other_user(self, user_service, db, regular_user, other_user):
        user_service.user_repository.get_user_by_id.return_value = other_user

        with pytest.raises(HTTPException) as exc:
            user_service.get_user_by_id(other_user.id, regular_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_not_found(self, user_service, db, admin_user):
        user_service.user_repository.get_user_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            user_service.get_user_by_id(999, admin_user, db)

        assert exc.value.status_code == 404


# --- get_user_by_email ---

class TestGetUserByEmail:
    def test_admin_can_access_any_email(self, user_service, db, admin_user, other_user):
        user_service.user_repository.get_user_by_email.return_value = other_user

        result = user_service.get_user_by_email(other_user.email, admin_user, db)

        assert result == other_user

    def test_user_can_access_own_email(self, user_service, db, regular_user):
        user_service.user_repository.get_user_by_email.return_value = regular_user

        result = user_service.get_user_by_email(regular_user.email, regular_user, db)

        assert result == regular_user

    def test_user_cannot_access_other_email(self, user_service, db, regular_user, other_user):
        with pytest.raises(HTTPException) as exc:
            user_service.get_user_by_email(other_user.email, regular_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_not_found(self, user_service, db, admin_user):
        user_service.user_repository.get_user_by_email.return_value = None

        with pytest.raises(HTTPException) as exc:
            user_service.get_user_by_email("notfound@example.com", admin_user, db)

        assert exc.value.status_code == 404


# --- get_user_by_username ---

class TestGetUserByUsername:
    def test_admin_can_access_any_username(self, user_service, db, admin_user, other_user):
        user_service.user_repository.get_user_by_username.return_value = other_user

        result = user_service.get_user_by_username(other_user.username, admin_user, db)

        assert result == other_user

    def test_user_can_access_own_username(self, user_service, db, regular_user):
        user_service.user_repository.get_user_by_username.return_value = regular_user

        result = user_service.get_user_by_username(regular_user.username, regular_user, db)

        assert result == regular_user

    def test_user_cannot_access_other_username(self, user_service, db, regular_user, other_user):
        with pytest.raises(HTTPException) as exc:
            user_service.get_user_by_username(other_user.username, regular_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_not_found(self, user_service, db, admin_user):
        user_service.user_repository.get_user_by_username.return_value = None

        with pytest.raises(HTTPException) as exc:
            user_service.get_user_by_username("ghost", admin_user, db)

        assert exc.value.status_code == 404
