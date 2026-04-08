import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from enums.user_roles import UserRoles
from models.conversation_model import Conversation
from models.user_model import User
from services.conversation_service import ConversationService


def make_user(id: int, role: UserRoles) -> User:
    user = MagicMock(spec=User)
    user.id = id
    user.role = role
    return user


def make_conversation(id: int, user_id: int, title: str) -> Conversation:
    conv = MagicMock(spec=Conversation)
    conv.id = id
    conv.user_id = user_id
    conv.title = title
    return conv


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def conversation_service():
    service = ConversationService()
    service.conversation_repository = MagicMock()
    return service


@pytest.fixture
def admin_user():
    return make_user(1, UserRoles.ADMIN)


@pytest.fixture
def regular_user():
    return make_user(2, UserRoles.USER)


@pytest.fixture
def other_user():
    return make_user(3, UserRoles.USER)


@pytest.fixture
def user_conversation():
    return make_conversation(10, 2, "Ma conversation")


# --- get_all_conversations ---

class TestGetAllConversations:
    def test_returns_all_conversations(self, conversation_service, db, user_conversation):
        conversation_service.conversation_repository.get_all_conversations.return_value = [user_conversation]

        result = conversation_service.get_all_conversations(db)

        assert result == [user_conversation]
        conversation_service.conversation_repository.get_all_conversations.assert_called_once_with(db)


# --- create_conversation ---

class TestCreateConversation:
    def test_user_can_create_own_conversation(self, conversation_service, db, regular_user):
        conversation_service.conversation_repository.exists_conversation_with_title_and_user_id.return_value = False
        conversation_service.conversation_repository.create_conversation.return_value = make_conversation(10, regular_user.id, "Titre")

        result = conversation_service.create_conversation(regular_user.id, "Titre", regular_user, db)

        assert result.user_id == regular_user.id
        conversation_service.conversation_repository.create_conversation.assert_called_once()

    def test_admin_can_create_for_any_user(self, conversation_service, db, admin_user, other_user):
        conversation_service.conversation_repository.exists_conversation_with_title_and_user_id.return_value = False
        conversation_service.conversation_repository.create_conversation.return_value = make_conversation(11, other_user.id, "Titre")

        result = conversation_service.create_conversation(other_user.id, "Titre", admin_user, db)

        assert result.user_id == other_user.id

    def test_user_cannot_create_for_other_user(self, conversation_service, db, regular_user, other_user):
        with pytest.raises(HTTPException) as exc:
            conversation_service.create_conversation(other_user.id, "Titre", regular_user, db)

        assert exc.value.status_code == 403

    def test_raises_400_if_title_already_exists(self, conversation_service, db, regular_user):
        conversation_service.conversation_repository.exists_conversation_with_title_and_user_id.return_value = True

        with pytest.raises(HTTPException) as exc:
            conversation_service.create_conversation(regular_user.id, "Titre existant", regular_user, db)

        assert exc.value.status_code == 400


# --- get_conversations_for_user ---

class TestGetConversationsForUser:
    def test_user_can_get_own_conversations(self, conversation_service, db, regular_user, user_conversation):
        conversation_service.conversation_repository.get_conversations_by_user_id.return_value = [user_conversation]

        result = conversation_service.get_conversations_for_user(regular_user.id, regular_user, db)

        assert result == [user_conversation]

    def test_admin_can_get_any_user_conversations(self, conversation_service, db, admin_user, regular_user, user_conversation):
        conversation_service.conversation_repository.get_conversations_by_user_id.return_value = [user_conversation]

        result = conversation_service.get_conversations_for_user(regular_user.id, admin_user, db)

        assert result == [user_conversation]

    def test_user_cannot_get_other_user_conversations(self, conversation_service, db, regular_user, other_user):
        with pytest.raises(HTTPException) as exc:
            conversation_service.get_conversations_for_user(other_user.id, regular_user, db)

        assert exc.value.status_code == 403


# --- get_conversation_by_id ---

class TestGetConversationById:
    def test_owner_can_get_conversation(self, conversation_service, db, regular_user, user_conversation):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        result = conversation_service.get_conversation_by_id(user_conversation.id, regular_user, db)

        assert result == user_conversation

    def test_admin_can_get_any_conversation(self, conversation_service, db, admin_user, user_conversation):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        result = conversation_service.get_conversation_by_id(user_conversation.id, admin_user, db)

        assert result == user_conversation

    def test_other_user_cannot_get_conversation(self, conversation_service, db, other_user, user_conversation):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        with pytest.raises(HTTPException) as exc:
            conversation_service.get_conversation_by_id(user_conversation.id, other_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_not_found(self, conversation_service, db, regular_user):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            conversation_service.get_conversation_by_id(999, regular_user, db)

        assert exc.value.status_code == 404


# --- update_conversation ---

class TestUpdateConversation:
    def test_owner_can_update_conversation(self, conversation_service, db, regular_user, user_conversation):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = user_conversation
        conversation_service.conversation_repository.exists_conversation_with_title_and_user_id.return_value = False
        conversation_service.conversation_repository.update_conversation.return_value = user_conversation

        result = conversation_service.update_conversation(user_conversation.id, "Nouveau titre", regular_user, db)

        assert result == user_conversation
        assert user_conversation.title == "Nouveau titre"

    def test_other_user_cannot_update_conversation(self, conversation_service, db, other_user, user_conversation):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        with pytest.raises(HTTPException) as exc:
            conversation_service.update_conversation(user_conversation.id, "Titre", other_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_not_found(self, conversation_service, db, regular_user):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            conversation_service.update_conversation(999, "Titre", regular_user, db)

        assert exc.value.status_code == 404

    def test_raises_400_if_title_already_exists(self, conversation_service, db, regular_user, user_conversation):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = user_conversation
        conversation_service.conversation_repository.exists_conversation_with_title_and_user_id.return_value = True

        with pytest.raises(HTTPException) as exc:
            conversation_service.update_conversation(user_conversation.id, "Titre existant", regular_user, db)

        assert exc.value.status_code == 400


# --- delete_conversation ---

class TestDeleteConversation:
    def test_owner_can_delete_conversation(self, conversation_service, db, regular_user, user_conversation):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = user_conversation
        conversation_service.conversation_repository.delete_conversation.return_value = True

        result = conversation_service.delete_conversation(user_conversation.id, regular_user, db)

        assert result is True
        conversation_service.conversation_repository.delete_conversation.assert_called_once_with(user_conversation.id, db)

    def test_other_user_cannot_delete_conversation(self, conversation_service, db, other_user, user_conversation):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        with pytest.raises(HTTPException) as exc:
            conversation_service.delete_conversation(user_conversation.id, other_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_not_found(self, conversation_service, db, regular_user):
        conversation_service.conversation_repository.get_conversation_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            conversation_service.delete_conversation(999, regular_user, db)

        assert exc.value.status_code == 404
