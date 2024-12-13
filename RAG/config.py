import os
from dotenv import load_dotenv

load_dotenv()

CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
EMBEDDING_MODEL = "voyage-multilingual-2"
PDF_FILES = ["rbf.pdf"]
CROSS_ENCODER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
LLAMA_BASE_URL = "http://localhost:11434"