from pydantic import BaseModel

class MetadataCreationRequest(BaseModel):
    '''Schéma pour la création d'une entrée de métadonnée.'''
    type: str
    source: str
    topic: str
    level: str
    language: str


class MetadataUpdateRequest(BaseModel):
    '''Schéma pour la mise à jour d'une entrée de métadonnée.'''
    type: str | None = None
    source: str | None = None
    topic: str | None = None
    level: str | None = None
    language: str | None = None
