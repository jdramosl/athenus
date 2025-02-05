from dotenv import load_dotenv
import logging
from loaders.pdf_loader import PDFLoaderService
from retrieval.retrieval_system import RetrievalSystem
from chat.handler import ChatHandler
import os


class App:
    def __init__(self):
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.pdf_files = ["rbf.pdf"]
        self.embedding_model = "voyage-multilingual-2"
        self.chat_model = os.getenv("CHAT_MODEL", "llama3.2")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))

    def initialize_loader_service(self):
        return PDFLoaderService(
            pdf_files=self.pdf_files,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

    def initialize_retrieval_system(self, all_docs):
        return RetrievalSystem(all_docs)

    def initialize_chat_handler(self, retrieval_system):
        return ChatHandler(
            retrieval_system=retrieval_system,
            chat_model=self.chat_model,
            cross_encoder_model='cross-encoder/ms-marco-MiniLM-L-6-v2'
        )
