from dotenv import load_dotenv
import logging
from loaders.pdf_loader import PDFLoaderService
from retrieval.retrieval_system import RetrievalSystem
from chat.handler import ChatHandler
import os


class App:
    """
    Clase principal de la aplicación.
    """
    def __init__(self):
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.pdf_files = ["rbf.pdf"]
        self.embedding_model = "voyage-multilingual-2"
        self.chat_model = os.getenv("CHAT_MODEL", "llama3.2")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))

    def run(self):
        loader_service = PDFLoaderService(
            pdf_files=self.pdf_files,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        all_docs = loader_service.load_pdfs()

        if not all_docs:
            print("No se cargaron documentos exitosamente. Por favor, verifica tus archivos PDF e inténtalo de nuevo.")
            return

        retrieval_system = RetrievalSystem(all_docs)
        if not retrieval_system.vectorstore or not retrieval_system.bm25l_retriever or not retrieval_system.tfidf_vectorizer:
            return

        chat_handler = ChatHandler(
            retrieval_system=retrieval_system,
            chat_model=self.chat_model,
            cross_encoder_model='cross-encoder/ms-marco-MiniLM-L-6-v2'
        )

        while True:
            query = input("\nHaz una pregunta (o escribe 'salir' para terminar): ")
            if not chat_handler.handle_query(query):
                break

if __name__ == "__main__":
    App().run()