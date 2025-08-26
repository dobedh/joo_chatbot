import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

# PDF path
PDF_PATH = BASE_DIR.parent / "Samsung_Electronics_Sustainability_Report_2025_KOR.pdf"

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Vector DB settings
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", str(DATA_DIR / "chroma_db"))

# Model settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Chunking settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# App settings
APP_PORT = int(os.getenv("APP_PORT", "8501"))
APP_HOST = os.getenv("APP_HOST", "localhost")