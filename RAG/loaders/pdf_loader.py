from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import os


class PDFLoaderService:
    """
    Servicio para cargar y procesar archivos PDF.
    """
    def __init__(self, pdf_files: List[str], chunk_size: int, chunk_overlap: int):
        self.pdf_files = pdf_files
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_pdfs(self) -> List[Document]:
            all_docs = []
            for pdf_file in self.pdf_files:
                try:
                    # Verify file exists and is in the allowed files list
                    if not os.path.exists(pdf_file):
                        logging.warning(f"File not found or not accessible: {pdf_file}")
                        continue

                    print(f"Loading PDF file: {pdf_file}")
                    loader = PyPDFLoader(pdf_file)
                    data = loader.load()
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap
                    )
                    docs = text_splitter.split_documents(data)
                    all_docs.extend(docs)
                    logging.info("Successfully loaded %s", pdf_file)
                except Exception as e:
                    logging.error("Error loading %s: %s", pdf_file, str(e))
            return all_docs
