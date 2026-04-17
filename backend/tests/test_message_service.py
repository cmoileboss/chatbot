import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from enums.sender_role import SenderRole
from enums.user_roles import UserRoles
from models.conversation_model import Conversation
from models.message_model import Message
from models.user_model import User
from services.message_service import MessageService


def make_user(id: int, role: UserRoles) -> User:
    user = MagicMock(spec=User)
    user.id = id
    user.role = role
    return user


def make_conversation(id: int, user_id: int) -> Conversation:
    conv = MagicMock(spec=Conversation)
    conv.id = id
    conv.user_id = user_id
    return conv


def make_message(id: int, conversation_id: int, role: SenderRole, content: str) -> Message:
    msg = MagicMock(spec=Message)
    msg.id = id
    msg.conversation_id = conversation_id
    msg.role = role
    msg.content = content
    return msg


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def message_service():
    service = MessageService()
    service.message_repository = MagicMock()
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
    return make_conversation(10, 2)  # owned by regular_user (id=2)


@pytest.fixture
def user_message(user_conversation):
    return make_message(100, user_conversation.id, SenderRole.USER, "Bonjour")


# --- get_messages_by_conversation_id ---

class TestGetMessagesByConversationId:
    def test_owner_can_get_messages(self, message_service, db, regular_user, user_conversation, user_message):
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation
        message_service.message_repository.get_messages_by_conversation_id.return_value = [user_message]

        result = message_service.get_messages_by_conversation_id(user_conversation.id, regular_user, db)

        assert result == [user_message]

    def test_admin_can_get_any_messages(self, message_service, db, admin_user, user_conversation, user_message):
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation
        message_service.message_repository.get_messages_by_conversation_id.return_value = [user_message]

        result = message_service.get_messages_by_conversation_id(user_conversation.id, admin_user, db)

        assert result == [user_message]

    def test_other_user_cannot_get_messages(self, message_service, db, other_user, user_conversation):
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        with pytest.raises(HTTPException) as exc:
            message_service.get_messages_by_conversation_id(user_conversation.id, other_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_conversation_not_found(self, message_service, db, regular_user):
        message_service.conversation_repository.get_conversation_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            message_service.get_messages_by_conversation_id(999, regular_user, db)

        assert exc.value.status_code == 404


# --- create_message ---

class TestCreateMessage:
    def test_owner_can_create_message(self, message_service, db, regular_user, user_conversation, user_message):
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation
        message_service.message_repository.create_message.return_value = user_message

        result = message_service.create_message(user_conversation.id, SenderRole.USER, "Bonjour", regular_user, db)

        assert result == user_message
        message_service.message_repository.create_message.assert_called_once()

    def test_other_user_cannot_create_message(self, message_service, db, other_user, user_conversation):
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        with pytest.raises(HTTPException) as exc:
            message_service.create_message(user_conversation.id, SenderRole.USER, "Bonjour", other_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_conversation_not_found(self, message_service, db, regular_user):
        message_service.conversation_repository.get_conversation_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            message_service.create_message(999, SenderRole.USER, "Bonjour", regular_user, db)

        assert exc.value.status_code == 404


# --- get_message_by_id ---

class TestGetMessageById:
    def test_owner_can_get_message(self, message_service, db, regular_user, user_conversation, user_message):
        message_service.message_repository.get_message_by_id.return_value = user_message
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        result = message_service.get_message_by_id(user_message.id, regular_user, db)

        assert result == user_message

    def test_other_user_cannot_get_message(self, message_service, db, other_user, user_conversation, user_message):
        message_service.message_repository.get_message_by_id.return_value = user_message
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        with pytest.raises(HTTPException) as exc:
            message_service.get_message_by_id(user_message.id, other_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_message_not_found(self, message_service, db, regular_user):
        message_service.message_repository.get_message_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            message_service.get_message_by_id(999, regular_user, db)

        assert exc.value.status_code == 404


# --- delete_message ---

class TestDeleteMessage:
    def test_owner_can_delete_message(self, message_service, db, regular_user, user_conversation, user_message):
        message_service.message_repository.get_message_by_id.return_value = user_message
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation
        message_service.message_repository.delete_message.return_value = True

        result = message_service.delete_message(user_message.id, regular_user, db)

        assert result is True
        message_service.message_repository.delete_message.assert_called_once_with(user_message.id, db)

    def test_other_user_cannot_delete_message(self, message_service, db, other_user, user_conversation, user_message):
        message_service.message_repository.get_message_by_id.return_value = user_message
        message_service.conversation_repository.get_conversation_by_id.return_value = user_conversation

        with pytest.raises(HTTPException) as exc:
            message_service.delete_message(user_message.id, other_user, db)

        assert exc.value.status_code == 403

    def test_raises_404_if_message_not_found(self, message_service, db, regular_user):
        message_service.message_repository.get_message_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            message_service.delete_message(999, regular_user, db)

        assert exc.value.status_code == 404
