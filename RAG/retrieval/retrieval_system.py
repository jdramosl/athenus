from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

from retrieval.bm25 import BM25LRetriever
from langchain.schema import Document


class RetrievalSystem:
    """
    Sistema de recuperación que integra vectores de embeddings, BM25L y TF-IDF.
    """
    def __init__(self, docs: List[Document]):
        self.docs = docs
        self.vectorstore = None
        self.bm25l_retriever = None
        self.tfidf_vectorizer = None
        self._initialize()

    def _initialize(self):
        try:
            print("Creando sistemas de recuperación...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            self.vectorstore = Chroma.from_documents(documents=self.docs, embedding=embeddings)
            doc_texts = [doc.page_content for doc in self.docs]
            self.bm25l_retriever = BM25LRetriever(doc_texts, k1=1.2, b=0.75, delta=0.5)
            self.tfidf_vectorizer = TfidfVectorizer().fit(doc_texts)
            logging.info("Sistemas de recuperación creados exitosamente")
        except Exception as e:
            logging.error("Error creando sistemas de recuperación: %s", str(e))
            print(f"Error creando sistemas de recuperación: {str(e)}")