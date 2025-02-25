from dotenv import load_dotenv
import logging
from loaders.pdf_loader import PDFLoaderService
from retrieval.retrieval_system import RetrievalSystem
from chat.handler import ChatHandler
from config.roles import ROLE_PDF_MAPPING, DEFAULT_ROLE
import os


class App:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(App, cls).__new__(cls)
        return cls._instance
    def __init__(self):
            if not self._initialized:
                load_dotenv()
                logging.basicConfig(level=logging.INFO)
                self.logger = logging.getLogger(__name__)
                self.embedding_model = "voyage-multilingual-2"
                self.chat_model = os.getenv("CHAT_MODEL", "llama3.2")
                self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
                self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
                self.role_handlers = {}
                self.initialize_role_handlers()
                self._initialized = True
    def initialize_role_handlers(self):
        """Initialize handlers for all roles at startup"""
        for role in ROLE_PDF_MAPPING.keys():
            try:
                self.logger.info(f"Initializing handler for role: {role}")

                # Get allowed PDFs for the role
                allowed_pdfs = self.get_pdf_files_for_role(role)

                # Initialize loader with allowed PDFs
                loader_service = PDFLoaderService(
                    pdf_files=allowed_pdfs,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )

                # Load documents
                docs = loader_service.load_pdfs()

                if not docs:
                    self.logger.warning(f"No documents found for role: {role}")
                    continue

                # Create role-specific retrieval system
                retrieval_system = self.initialize_retrieval_system(docs, role)
                chat_handler = self.initialize_chat_handler(retrieval_system)

                # Store the handler
                self.role_handlers[role] = chat_handler
                self.logger.info(f"Successfully initialized handler for role: {role}")

            except Exception as e:
                self.logger.error(f"Error initializing handler for role {role}: {str(e)}")
    def get_pdf_files_for_role(self, role: str) -> list:
        """Get the list of PDF files accessible for a specific role"""
        if role not in ROLE_PDF_MAPPING:
            self.logger.warning(f"Unknown role: {role}. Using default role.")
            role = DEFAULT_ROLE
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
        try:
            # Always create a new loader for each request to ensure fresh document access
            # Get allowed PDFs for the role
            allowed_pdfs = self.get_pdf_files_for_role(role)

            # Initialize loader with only allowed PDFs
            loader_service = PDFLoaderService(
                pdf_files=allowed_pdfs,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )

            # Load only allowed documents
            docs = loader_service.load_pdfs()

            if not docs:
                self.logger.warning(f"No accessible documents found for role: {role}")
                return None

            # Create role-specific retrieval system
            retrieval_system = self.initialize_retrieval_system(docs, role)
            chat_handler = self.initialize_chat_handler(retrieval_system)

            return chat_handler

        except Exception as e:
            self.logger.error(f"Error creating loader for role {role}: {str(e)}")
            return None

    def initialize_retrieval_system(self, all_docs, role):
            return RetrievalSystem(all_docs, role)

    def initialize_chat_handler(self, retrieval_system):
        return ChatHandler(
            retrieval_system=retrieval_system,
            chat_model=self.chat_model,
            cross_encoder_model='cross-encoder/ms-marco-MiniLM-L-6-v2'
        )
    def get_chat_handler(self, role: str):
        """Get the appropriate chat handler for a role"""
        if role not in self.role_handlers:
            self.logger.warning(f"No handler found for role: {role}. Using default role.")
            role = DEFAULT_ROLE
        return self.role_handlers.get(role)
