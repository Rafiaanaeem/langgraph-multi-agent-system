import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)
class Config:
    """Centralized configuration management for the multi-agent system."""
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    MODEL_NAME: str = "llama-3.1-8b-instant"
    CHROMA_PERSIST_DIR: str = "C:/face_recognition/chroma_db/arcface_db"
    COLLECTION_NAME: str = "arcface_faces"
    COSINE_THRESHOLD: float = 0.60
    EMBEDDING_DIM: int = 512
    
    # Renamed to FACE_MODEL_NAME to avoid conflicting with your LLM MODEL_NAME
    FACE_MODEL_NAME: str = "buffalo_l" 
    DET_SIZE: tuple = (640, 640)

