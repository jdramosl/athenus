import asyncio
import json
import logging
from typing import List, Tuple
import heapq
#import Document from RAG/retrieval/retrieval_system.py
from langchain.schema import Document

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import ConversationSummaryBufferMemory
from langchain_ollama import OllamaLLM
from sentence_transformers import CrossEncoder

from retrieval.retrieval_system import RetrievalSystem  # Asegúrate de que la ruta de importación es correcta


class ChatHandler:
    """
    Manejador de interacciones de chat con el usuario.
    """
    def __init__(self, retrieval_system: RetrievalSystem, chat_model: str, cross_encoder_model: str):
        self.retrieval_system = retrieval_system
        self.chat_model = chat_model
        self.cross_encoder = CrossEncoder(cross_encoder_model)
        self.llm = OllamaLLM(
            model=self.chat_model,
            temperature=0.0,
            callbacks=[StreamingStdOutCallbackHandler()],
            base_url="http://localhost:11434"
        )
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=50,
            input_key="question",
            memory_key="chat_history",
            return_messages=True
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Use the following context to answer the question in Spanish, paying close attention to the question details, thinking step by step, and providing a complete response."),
            ("human", "Context: {context}"),
            ("human", "Chat history: {chat_history}"),
            ("human", "Question: {question}")
        ])
        self.chain = (
            {
                "context": RunnablePassthrough(),
                "question": RunnablePassthrough(),
                "chat_history": lambda x: self.memory.load_memory_variables({})["chat_history"]
            }
            | self.prompt
            | self.llm
        )
        self.messages = []

    async def get_relevant_context(self, query: str) -> str:
        weighted_history = self.weight_chat_history()
        combined_query = f"{query} {weighted_history}"

        vector_results = await self.vector_search(combined_query)
        bm25l_results = await self.bm25l_search(combined_query)

        if not vector_results and not bm25l_results:
            logging.warning("Ambas búsquedas, vectorial y BM25L, fallaron. Recurriendo a búsqueda por palabras clave.")
            return self.fallback_keyword_search(combined_query)

        combined_results = []
        for doc in vector_results:
            heapq.heappush(combined_results, (-0.6, doc.page_content))

        for idx, score in bm25l_results:
            doc_content = self.retrieval_system.docs[idx].page_content
            heapq.heappush(combined_results, (-0.3 * score, doc_content))

        tfidf_scores = self.retrieval_system.tfidf_vectorizer.transform([combined_query]).toarray()[0]
        for idx, doc in enumerate(self.retrieval_system.docs):
            doc_content = doc.page_content
            if any(doc_content == content for _, content in combined_results):
                heapq.heappush(combined_results, (-0.1 * tfidf_scores[idx], doc_content))

        top_results = heapq.nsmallest(10, combined_results)
        docs_to_rerank = [doc for _, doc in top_results]
        original_scores = [-score for score, _ in top_results]

        reranked_docs = self.rerank_results(docs_to_rerank, combined_query, original_scores)
        return "\n".join(reranked_docs[:5])

    async def vector_search(self, query: str) -> List[Document]:
        try:
            return self.retrieval_system.vectorstore.similarity_search(query, k=10)
        except Exception as e:
            logging.error(f"Búsqueda vectorial fallida: {str(e)}")
            return []

    async def bm25l_search(self, query: str) -> List[Tuple[int, float]]:
        try:
            return self.retrieval_system.bm25l_retriever.retrieve(query, top_k=10)
        except Exception as e:
            logging.error(f"Búsqueda BM25L fallida: {str(e)}")
            return []

    def weight_chat_history(self, max_messages: int = 2, decay_factor: float = 0.9) -> str:
        recent_history = self.messages[-max_messages:]
        weighted_history = []
        for i, message in enumerate(reversed(recent_history)):
            weight = decay_factor ** i
            weighted_history.append(f"{weight:.2f} * {message['content']}")
        return " ".join(reversed(weighted_history))

    def rerank_results(self, docs: List[str], query: str, original_scores: List[float]) -> List[str]:
        pairs = [[query, doc] for doc in docs]
        scores = self.cross_encoder.predict(pairs)
        combined_scores = [0.7 * new_score + 0.3 * original_score for new_score, original_score in zip(scores, original_scores)]
        return [doc for _, doc in sorted(zip(combined_scores, docs), reverse=True)]

    def fallback_keyword_search(self, query: str) -> str:
        keywords = query.lower().split()
        relevant_docs = []
        for doc in self.retrieval_system.docs:
            if any(keyword in doc.page_content.lower() for keyword in keywords):
                relevant_docs.append(doc.page_content)
        if not relevant_docs:
            return "No pude encontrar información relevante. ¿Puedes reformular tu pregunta?"
        return "\n".join(relevant_docs[:3])

    def save_feedback(self, query: str, answer: str, feedback: int):
        feedback_data = {
            "query": query,
            "answer": answer,
            "feedback": feedback
        }
        with open("feedback_log.json", "a") as f:
            json.dump(feedback_data, f)
            f.write("\n")

    def handle_query(self, query: str):
        if query.lower() == 'salir':
            return False

        self.messages.append({"role": "user", "content": query})
        try:
            print("\nAnalizando documentos...")
            context = asyncio.run(self.get_relevant_context(query))
            formatted_prompt = self.prompt.format(
                context=context,
                question=query,
                chat_history=self.memory.load_memory_variables({})["chat_history"]
            )
            print("\nPrompt enviado al modelo:")
            print(formatted_prompt)
            response = self.chain.invoke({"context": context, "question": query})
            self.memory.save_context({"question": query}, {"output": response})
            print("\nRespuesta:", response)
            self.messages.append({"role": "assistant", "content": response})

            feedback = input("\n¿Deseas calificar la respuesta? (1-5, o presiona Enter para saltar): ")
            if feedback.isdigit() and 1 <= int(feedback) <= 5:
                self.save_feedback(query, response, int(feedback))

        except Exception as e:
            logging.error("Error procesando la consulta: %s", str(e))
            fallback = self.fallback_keyword_search(query)
            print(f"\nError: Lo siento, pero encontré un error al procesar tu consulta. Esto es lo que encontré basado en una búsqueda por palabras clave: {fallback}")
        return True
