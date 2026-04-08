from sqlalchemy.orm import Session

from models.metadata_model import Metadata


class MetadataRepository:
    '''Repository for managing metadata in the database.'''

    def get_all(self, db: Session) -> list[Metadata]:
        '''Get all metadata entries.'''
        return db.query(Metadata).all()

    def get_by_id(self, metadata_id: int, db: Session) -> Metadata | None:
        '''Get a metadata entry by its ID.'''
        return db.query(Metadata).filter(Metadata.id == metadata_id).first()

    def create(self, metadata: Metadata, db: Session) -> Metadata:
        '''Create a new metadata entry.'''
        db.add(metadata)
        db.commit()
        db.refresh(metadata)
        return metadata

    def update(self, metadata: Metadata, db: Session) -> Metadata:
        '''Update an existing metadata entry.'''
        db.commit()
        db.refresh(metadata)
        return metadata

    def delete(self, metadata_id: int, db: Session) -> bool:
        '''Delete a metadata entry by its ID.'''
        metadata = self.get_by_id(metadata_id, db)
        if metadata:
            db.delete(metadata)
            db.commit()
            return True
        return False
