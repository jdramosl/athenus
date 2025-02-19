from dotenv import load_dotenv
import logging
from loaders.pdf_loader import PDFLoaderService
from retrieval.retrieval_system import RetrievalSystem
from chat.handler import ChatHandler
from config.roles import ROLE_PDF_MAPPING, DEFAULT_ROLE
import os


class App:
    def __init__(self):
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.pdf_files = ["rbf.pdf","art2.pdf","art1.pdf"]
        self.embedding_model = "voyage-multilingual-2"
        self.chat_model = os.getenv("CHAT_MODEL", "llama3.2")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
        self.role_loaders = {}

    def get_pdf_files_for_role(self, role: str) -> list:
            """Get the list of PDF files accessible for a specific role"""
            if role not in ROLE_PDF_MAPPING:
                self.logger.warning(f"Unknown role: {role}. Using default role.")
                return ROLE_PDF_MAPPING[DEFAULT_ROLE]
            return ROLE_PDF_MAPPING[role]

    def initialize_loader_service(self, role: str):
            """Initialize loader service for a specific role"""
            pdf_files = self.get_pdf_files_for_role(role)
            return PDFLoaderService(
                pdf_files=pdf_files,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
    def get_or_create_role_loader(self, role: str):
            """Get or create a loader for a specific role"""
            if role not in self.role_loaders:
                loader_service = self.initialize_loader_service(role)
                docs = loader_service.load_pdfs()
                retrieval_system = self.initialize_retrieval_system(docs)
                chat_handler = self.initialize_chat_handler(retrieval_system)
                self.role_loaders[role] = chat_handler
            return self.role_loaders[role]

    def initialize_retrieval_system(self, all_docs):
        return RetrievalSystem(all_docs)

    def initialize_chat_handler(self, retrieval_system):
        return ChatHandler(
            retrieval_system=retrieval_system,
            chat_model=self.chat_model,
            cross_encoder_model='cross-encoder/ms-marco-MiniLM-L-6-v2'
        )
