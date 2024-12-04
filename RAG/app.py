import streamlit as st
import os
import logging
import asyncio
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.llms import Ollama
from langchain_chroma import Chroma
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import ConversationSummaryBufferMemory
from typing import List, Tuple, Optional
from langchain.schema import Document
from sentence_transformers import CrossEncoder
import numpy as np
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from collections import defaultdict
import heapq
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain_community.embeddings import HuggingFaceEmbeddings

#ESTA VERSIÓN USA EL MODELO DE EMBEDDINGS "voyage-multilingual-2" DE VOYAGE AI Y EL MODELO DE CHAT "gemini-1.5-flash" DE GOOGLE GENAI
#además usa el modelo de cross-encoder "cross-encoder/ms-marco-MiniLM-L-6 y - NO TIENE - iterative_retrieval para obtener más información relevante


# Cargar variables de entorno y configurar el registro
load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuración de la aplicación Streamlit
st.set_page_config(page_title="Sistema de Recuperación de Documentos", layout="wide")
st.title("Sistema de Recuperación de Documentos")

# Configuración de archivos PDF y modelos
PDF_FILES = ["rbf.pdf"]
EMBEDDING_MODEL = "voyage-multilingual-2"
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))



# Clase para el algoritmo BM25L
class BM25L:
    def __init__(self, corpus, k1=1.5, b=0.75, delta=0.5):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.delta = delta
        self.avg_doc_len = sum(len(doc.split()) for doc in corpus) / len(corpus)
        self.doc_freqs = []
        self.idf = defaultdict(float)
        self.doc_len = []
        self.corpus_size = len(corpus)
        self._initialize()

    def _initialize(self):
        for document in self.corpus:
            words = document.split()
            self.doc_len.append(len(words))
            freq_dict = defaultdict(int)
            for word in words:
                freq_dict[word] += 1
            self.doc_freqs.append(freq_dict)
            for word in freq_dict:
                self.idf[word] += 1

        for word, freq in self.idf.items():
            self.idf[word] = np.log((self.corpus_size - freq + 0.5) / (freq + 0.5))

    def get_scores(self, query):
        scores = [0] * self.corpus_size
        query_words = query.split()
        q_freqs = defaultdict(int)
        for word in query_words:
            q_freqs[word] += 1

        for i, doc in enumerate(self.corpus):
            for word in query_words:
                if word not in self.doc_freqs[i]:
                    continue
                freq = self.doc_freqs[i][word]
                numerator = self.idf[word] * freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avg_doc_len)
                scores[i] += (numerator / denominator) + self.delta

        return scores

# Clase para el recuperador BM25L
class BM25LRetriever:
    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75, delta: float = 0.5):
        self.documents = documents
        self.bm25 = BM25L(self.documents, k1=k1, b=b, delta=delta)

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        doc_scores = self.bm25.get_scores(query)
        return heapq.nlargest(top_k, enumerate(doc_scores), key=lambda x: x[1])

# Función para cargar archivos PDF
@st.cache_data
def load_pdf(pdf_file: str) -> List[Document]:
    try:
        st.text(f"Cargando archivo PDF: {pdf_file}")
        loader = PyPDFLoader(pdf_file)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        docs = text_splitter.split_documents(data)
        logger.info("Cargado exitosamente %s", pdf_file)
        st.success(f"Cargado exitosamente {pdf_file}")
        return docs
    except Exception as e:
        logger.error("Error cargando %s: %s", pdf_file, str(e))
        st.error(f"Error cargando {pdf_file}: {str(e)}")
        return []

# Función para calcular pesos TF-IDF
def compute_tfidf_weights(docs: List[str]) -> TfidfVectorizer:
    vectorizer = TfidfVectorizer()
    vectorizer.fit(docs)
    return vectorizer

@st.cache_resource
def create_retrieval_systems(_docs: List[Document]) -> Tuple[Optional[Chroma], Optional[BM25LRetriever], Optional[List[Document]], Optional[TfidfVectorizer]]:
    try:
        with st.spinner("Creando sistemas de recuperación..."):
            # Usar HuggingFaceEmbeddings en lugar de VoyageAIEmbeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )

            vectorstore = Chroma.from_documents(
                documents=_docs,
                embedding=embeddings
            )
            doc_texts = [doc.page_content for doc in _docs]
            bm25l_retriever = BM25LRetriever(doc_texts, k1=1.2, b=0.75, delta=0.5)
            tfidf_vectorizer = compute_tfidf_weights(doc_texts)
        logger.info("Sistemas de recuperación creados exitosamente")
        return vectorstore, bm25l_retriever, _docs, tfidf_vectorizer
    except Exception as e:
        logger.error("Error creando sistemas de recuperación: %s", str(e))
        st.error(f"Error creando sistemas de recuperación: {str(e)}")
        return None, None, None, None
# Función para cargar el CrossEncoder
@st.cache_resource
def load_cross_encoder():
    return CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Función para ponderar el historial de chat
def weight_chat_history(chat_history: List[dict], max_messages: int = 2, decay_factor: float = 0.9) -> str:
    recent_history = chat_history[-max_messages:]
    weighted_history = []
    for i, message in enumerate(reversed(recent_history)):
        weight = decay_factor ** i
        weighted_history.append(f"{weight:.2f} * {message['content']}")
    return " ".join(reversed(weighted_history))

# Función para reordenar resultados usando CrossEncoder
def rerank_results(docs: List[str], query: str, cross_encoder: CrossEncoder, original_scores: List[float]) -> List[str]:
    pairs = [[query, doc] for doc in docs]
    scores = cross_encoder.predict(pairs)
    combined_scores = [0.7 * new_score + 0.3 * original_score for new_score, original_score in zip(scores, original_scores)]
    return [doc for _, doc in sorted(zip(combined_scores, docs), reverse=True)]

# Función de búsqueda por palabras clave como fallback (Esta función se utiliza como una alternativa cuando otros métodos de búsqueda más avanzados fallan)
def fallback_keyword_search(docs: List[Document], query: str) -> str:
    keywords = query.lower().split()
    relevant_docs = []
    for doc in docs:
        if any(keyword in doc.page_content.lower() for keyword in keywords):
            relevant_docs.append(doc.page_content)
    if not relevant_docs:
        return "No pude encontrar información relevante. ¿Puedes reformular tu pregunta?"
    return "\n".join(relevant_docs[:3])

# Función para obtener el contexto relevante
async def get_relevant_context(vectorstore: Chroma, bm25l_retriever: BM25LRetriever, docs: List[Document], tfidf_vectorizer: TfidfVectorizer, query: str, chat_history: List[dict], cross_encoder: CrossEncoder) -> str:
    try:
        weighted_history = weight_chat_history(chat_history)
        combined_query = query + " " + weighted_history

        async def vector_search():
            try:
                return vectorstore.similarity_search(combined_query, k=10)
            except Exception as e:
                logger.error(f"Búsqueda vectorial fallida: {str(e)}")
                return []

        async def bm25l_search():
            try:
                return bm25l_retriever.retrieve(combined_query, top_k=10)
            except Exception as e:
                logger.error(f"Búsqueda BM25L fallida: {str(e)}")
                return []

        vector_results, bm25l_results = await asyncio.gather(vector_search(), bm25l_search())

        if not vector_results and not bm25l_results:
            logger.warning("Ambas búsquedas, vectorial y BM25L, fallaron. Recurriendo a búsqueda por palabras clave.")
            return fallback_keyword_search(docs, combined_query)

        combined_results = []
        for doc in vector_results:
            heapq.heappush(combined_results, (-0.6, doc.page_content))

        for idx, score in bm25l_results:
            doc_content = docs[idx].page_content
            heapq.heappush(combined_results, (-0.3 * score, doc_content))

        tfidf_scores = tfidf_vectorizer.transform([combined_query]).toarray()[0]
        for idx, doc in enumerate(docs):
            doc_content = doc.page_content
            if any(doc_content == content for _, content in combined_results):
                heapq.heappush(combined_results, (-0.1 * tfidf_scores[idx], doc_content))

        top_results = heapq.nsmallest(10, combined_results)
        docs_to_rerank = [doc for _, doc in top_results]
        original_scores = [-score for score, _ in top_results]

        reranked_docs = rerank_results(docs_to_rerank, combined_query, cross_encoder, original_scores)

        return "\n".join(reranked_docs[:5])

    except Exception as e:
        logger.error(f"Error en get_relevant_context: {str(e)}")
        return fallback_keyword_search(docs, query)

# Función para guardar retroalimentación
def save_feedback(query: str, answer: str, feedback: int):
    feedback_data = {
        "query": query,
        "answer": answer,
        "feedback": feedback
    }
    with open("feedback_log.json", "a") as f:
        json.dump(feedback_data, f)
        f.write("\n")

# Función principal de la aplicación
def main():
    all_docs = []
    for pdf_file in PDF_FILES:
        all_docs.extend(load_pdf(pdf_file))

    if not all_docs:
        st.error("No se cargaron documentos exitosamente. Por favor, verifica tus archivos PDF e inténtalo de nuevo.")
        return

    vectorstore, bm25l_retriever, docs, tfidf_vectorizer = create_retrieval_systems(all_docs)
    if not vectorstore or not bm25l_retriever or not tfidf_vectorizer:
        return

    streaming_handler = StreamingStdOutCallbackHandler()
    llm = Ollama(
        model="llama3.2",
        temperature=0.0,
        callbacks=[streaming_handler],
        base_url="http://localhost:11434"  # o la URL que corresponda
    )
    cross_encoder = load_cross_encoder()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente útil. Usa el siguiente contexto para responder la pregunta, prestando mucha atención a los detalles de la pregunta, pensando paso a paso y dando una respuesta completa."),
        ("human", "Contexto: {context}"),
        ("human", "Historial de chat: {chat_history}"),
        ("human", "Pregunta: {question}")
    ])
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=50,
        input_key="question",
        memory_key="chat_history",
        return_messages=True
    )
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True,
        output_key="answer"
    )

    st.subheader("Haz una pregunta sobre los documentos")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input("Tu pregunta sobre los documentos:"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                with st.spinner("Analizando documentos..."):
                    context = asyncio.run(get_relevant_context(vectorstore, bm25l_retriever, docs, tfidf_vectorizer, query, st.session_state.messages, cross_encoder))

                    response = llm_chain.predict(context=context, question=query)
                    full_response = response
                    message_placeholder.markdown(full_response)
            except Exception as e:
                logger.error("Error procesando la consulta: %s", str(e))
                full_response = f"Lo siento, pero encontré un error al procesar tu consulta. Esto es lo que encontré basado en una búsqueda por palabras clave: {fallback_keyword_search(docs, query)}"
                message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Mecanismo de retroalimentación
    if st.button("Enviar Retroalimentación"):
        feedback = st.slider("Califica la calidad de la respuesta (1-5)", 1, 5, 3)
        save_feedback(query, full_response, feedback)
        st.success("¡Gracias por tu retroalimentación!")

if __name__ == "__main__":
    main()
