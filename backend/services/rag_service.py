import os
import tempfile

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

CHROMA_DIR = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md'}


class RagService:
    '''Service de gestion du RAG (Retrieval-Augmented Generation).'''

    def __init__(self):
        self.embeddings = OllamaEmbeddings(model='nomic-embed-text')
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        self.score_threshold = 1.2  # distance L2 max (plus bas = plus pertinent)

    def _get_vectorstore(self, collection: str) -> Chroma:
        safe_name = f"user_{collection}"
        return Chroma(
            collection_name=safe_name,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DIR,
        )

    def ingest_file(self, file_path: str, original_filename: str, collection: str = 'default') -> int:
        '''Indexe un fichier dans ChromaDB en stockant le nom original dans les métadonnées.
        Returns:
            Le nombre de chunks indexés.
        '''
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext == '.docx':
            loader = Docx2txtLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding='utf-8')

        docs = loader.load()
        chunks = self.text_splitter.split_documents(docs)
        # Surcharger la métadonnée source avec le vrai nom de fichier
        for chunk in chunks:
            chunk.metadata['source'] = original_filename
        vectorstore = self._get_vectorstore(collection)
        vectorstore.add_documents(chunks)
        return len(chunks)

    def list_documents(self, collection: str) -> list[dict]:
        '''Retourne la liste des documents indexés avec leur nombre de chunks.
        Returns:
            Liste de dicts {"filename": str, "chunks": int}
        '''
        try:
            vectorstore = self._get_vectorstore(collection)
            result = vectorstore._collection.get(include=["metadatas"])
            counts: dict[str, int] = {}
            for meta in result.get("metadatas", []):
                name = (meta or {}).get("source", "inconnu")
                counts[name] = counts.get(name, 0) + 1
            return [{"filename": name, "chunks": count} for name, count in sorted(counts.items())]
        except Exception:
            return []

    def delete_document(self, filename: str, collection: str) -> int:
        '''Supprime tous les chunks d'un fichier donné. Retourne le nombre de chunks supprimés.'''
        try:
            vectorstore = self._get_vectorstore(collection)
            result = vectorstore._collection.get(
                where={"source": filename},
                include=["metadatas"],
            )
            ids = result.get("ids", [])
            if ids:
                vectorstore._collection.delete(ids=ids)
            return len(ids)
        except Exception:
            return 0

    def retrieve_context(self, query: str, collection: str = 'default', k: int = 5) -> str:
        '''Recherche les chunks les plus pertinents, filtre par score de pertinence.
        Returns:
            Le contexte sous forme de texte concaténé, ou chaîne vide si aucun chunk pertinent.
        '''
        vectorstore = self._get_vectorstore(collection)
        results = vectorstore.similarity_search_with_score(query, k=k)
        # Filtrer les chunks trop éloignés sémantiquement
        relevant = [doc for doc, score in results if score <= self.score_threshold]
        return '\n\n'.join(doc.page_content for doc in relevant)

    def has_documents(self, collection: str) -> bool:
        '''Vérifie si la collection contient des documents.'''
        try:
            vectorstore = self._get_vectorstore(collection)
            return vectorstore._collection.count() > 0
        except Exception:
            return False

    def reset_collection(self, collection: str) -> None:
        '''Supprime tous les documents de la collection ChromaDB d'un utilisateur.'''
        import chromadb
        safe_name = f"user_{collection}"
        client = chromadb.PersistentClient(path=os.path.abspath(CHROMA_DIR))
        try:
            client.delete_collection(safe_name)
        except Exception:
            pass
