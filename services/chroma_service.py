import chromadb
from typing import List, Dict, Any
from config import Config
from fastapi import HTTPException, status
from pathlib import Path
print(">>>>>>>> USING CHROMA_SERVICE.PY <<<<<<<<")

class ChromaService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=Config.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        if self.collection.count() > 0:
                    print(self.collection.peek())
        
        print("Database Path:", Config.CHROMA_PERSIST_DIR)
        print("Collection Name:", Config.COLLECTION_NAME)
        print("Total Embeddings:", self.collection.count())
        print("Resolved Path:", Path(Config.CHROMA_PERSIST_DIR).resolve())
        print("\n===== ALL COLLECTIONS =====")
        collections = self.client.list_collections()
        for c in collections:
             print(f"Collection: {c.name}")
             print(f"Count: {c.count()}")
             
    def upsert_face(self, face_id: str, embedding: List[float], metadata: Dict[str, Any]):
        try:
            self.collection.upsert(
                ids=[face_id],
                embeddings=[embedding],
                metadatas=[metadata]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database upsert error: {str(e)}"
            )
    def query_nearest(self, query_embedding: List[float]) -> Dict[str, Any]:
        try:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1,
                include=["metadatas", "distances"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database query error: {str(e)}"
            )
        
chroma_db = ChromaService()

