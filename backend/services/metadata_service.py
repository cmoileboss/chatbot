from sqlalchemy.orm import Session

from fastapi import HTTPException

from models.metadata_model import Metadata
from repositories.metadata_repository import MetadataRepository
from schemas.metadata_request import MetadataCreationRequest, MetadataUpdateRequest


class MetadataService:
    '''Service de gestion des métadonnées.'''

    def __init__(self):
        self.metadata_repository = MetadataRepository()

    def get_all(self, db: Session) -> list[Metadata]:
        '''Get all metadata entries.'''
        return self.metadata_repository.get_all(db)

    def get_by_id(self, metadata_id: int, db: Session) -> Metadata:
        '''Get a metadata entry by its ID.'''
        metadata = self.metadata_repository.get_by_id(metadata_id, db)
        if metadata is None:
            raise HTTPException(status_code=404, detail="Métadonnée non trouvée")
        return metadata

    def create(self, request: MetadataCreationRequest, db: Session) -> Metadata:
        '''Create a new metadata entry.'''
        metadata = Metadata(
            type=request.type,
            source=request.source,
            topic=request.topic,
            level=request.level,
            language=request.language,
        )
        return self.metadata_repository.create(metadata, db)

    def update(self, metadata_id: int, request: MetadataUpdateRequest, db: Session) -> Metadata:
        '''Update an existing metadata entry.'''
        metadata = self.metadata_repository.get_by_id(metadata_id, db)
        if metadata is None:
            raise HTTPException(status_code=404, detail="Métadonnée non trouvée")
        if request.type is not None:
            metadata.type = request.type
        if request.source is not None:
            metadata.source = request.source
        if request.topic is not None:
            metadata.topic = request.topic
        if request.level is not None:
            metadata.level = request.level
        if request.language is not None:
            metadata.language = request.language
        return self.metadata_repository.update(metadata, db)

    def delete(self, metadata_id: int, db: Session) -> bool:
        '''Delete a metadata entry by its ID.'''
        if self.metadata_repository.get_by_id(metadata_id, db) is None:
            raise HTTPException(status_code=404, detail="Métadonnée non trouvée")
        return self.metadata_repository.delete(metadata_id, db)
