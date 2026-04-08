import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from models.metadata_model import Metadata
from schemas.metadata_request import MetadataCreationRequest, MetadataUpdateRequest
from services.metadata_service import MetadataService


def make_metadata(id: int, type: str = "doc", source: str = "web", topic: str = "python", level: str = "beginner", language: str = "fr") -> Metadata:
    metadata = MagicMock(spec=Metadata)
    metadata.id = id
    metadata.type = type
    metadata.source = source
    metadata.topic = topic
    metadata.level = level
    metadata.language = language
    return metadata


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def metadata_service():
    service = MetadataService()
    service.metadata_repository = MagicMock()
    return service


@pytest.fixture
def existing_metadata():
    return make_metadata(1)


# --- get_all ---

class TestGetAll:
    def test_returns_all_entries(self, metadata_service, db, existing_metadata):
        metadata_service.metadata_repository.get_all.return_value = [existing_metadata]

        result = metadata_service.get_all(db)

        assert result == [existing_metadata]
        metadata_service.metadata_repository.get_all.assert_called_once_with(db)

    def test_returns_empty_list(self, metadata_service, db):
        metadata_service.metadata_repository.get_all.return_value = []

        result = metadata_service.get_all(db)

        assert result == []


# --- get_by_id ---

class TestGetById:
    def test_returns_metadata_if_found(self, metadata_service, db, existing_metadata):
        metadata_service.metadata_repository.get_by_id.return_value = existing_metadata

        result = metadata_service.get_by_id(1, db)

        assert result == existing_metadata
        metadata_service.metadata_repository.get_by_id.assert_called_once_with(1, db)

    def test_raises_404_if_not_found(self, metadata_service, db):
        metadata_service.metadata_repository.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            metadata_service.get_by_id(999, db)

        assert exc.value.status_code == 404


# --- create ---

class TestCreate:
    def test_creates_metadata_successfully(self, metadata_service, db, existing_metadata):
        metadata_service.metadata_repository.create.return_value = existing_metadata
        request = MetadataCreationRequest(type="doc", source="web", topic="python", level="beginner", language="fr")

        result = metadata_service.create(request, db)

        assert result == existing_metadata
        metadata_service.metadata_repository.create.assert_called_once()
        created = metadata_service.metadata_repository.create.call_args[0][0]
        assert created.type == "doc"
        assert created.source == "web"
        assert created.topic == "python"
        assert created.level == "beginner"
        assert created.language == "fr"


# --- update ---

class TestUpdate:
    def test_updates_only_provided_fields(self, metadata_service, db, existing_metadata):
        metadata_service.metadata_repository.get_by_id.return_value = existing_metadata
        metadata_service.metadata_repository.update.return_value = existing_metadata
        request = MetadataUpdateRequest(topic="fastapi", level="advanced")

        result = metadata_service.update(1, request, db)

        assert result == existing_metadata
        assert existing_metadata.topic == "fastapi"
        assert existing_metadata.level == "advanced"
        # Champs non fournis ne sont pas modifiés
        assert existing_metadata.type == "doc"
        assert existing_metadata.language == "fr"

    def test_raises_404_if_not_found(self, metadata_service, db):
        metadata_service.metadata_repository.get_by_id.return_value = None
        request = MetadataUpdateRequest(topic="fastapi")

        with pytest.raises(HTTPException) as exc:
            metadata_service.update(999, request, db)

        assert exc.value.status_code == 404
        metadata_service.metadata_repository.update.assert_not_called()


# --- delete ---

class TestDelete:
    def test_deletes_successfully(self, metadata_service, db, existing_metadata):
        metadata_service.metadata_repository.get_by_id.return_value = existing_metadata
        metadata_service.metadata_repository.delete.return_value = True

        result = metadata_service.delete(1, db)

        assert result is True
        metadata_service.metadata_repository.delete.assert_called_once_with(1, db)

    def test_raises_404_if_not_found(self, metadata_service, db):
        metadata_service.metadata_repository.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            metadata_service.delete(999, db)

        assert exc.value.status_code == 404
        metadata_service.metadata_repository.delete.assert_not_called()
