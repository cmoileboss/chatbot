from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv
import os



# Charger les variables d'environnement à partir du fichier .env
load_dotenv()
USER = os.getenv('USER_POSTGRES_BD')
PASSWORD = os.getenv('PASSWORD_POSTGRES_BD')
SERVER = os.getenv('HOST_POSTGRES_BD')
PORT = os.getenv('PORT_POSTGRES_BD')
DB_NAME = os.getenv('NAME_POSTGRES_DB')

# Configuration de la connexion à PostgreSQL
# autocommit False : chaque opération n'est pas immédiatement validée dans la base de données.
# autoflush False : les modifications ne sont pas automatiquement envoyées à la base de données avant une requête.
DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
postgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_postgres_db():
    '''Obtenir une session de base de données PostgreSQL'''
    db = postgresSessionLocal()
    try:
        yield db
    finally:
        db.close()