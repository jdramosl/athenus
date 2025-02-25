from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv
from config.roles import DEFAULT_ROLE, ROLE_PDF_MAPPING
from app import App
from chat.handler import ChatHandler
import logging

# Modelo Pydantic
class Query(BaseModel):
    text: str
    role: str = DEFAULT_ROLE
    userId: str             # <-- Campo añadido para usuario
    feedback: Optional[int] = None

class Response(BaseModel):
    answer: str
    context: str

app = FastAPI(title="RAG API", description="API para el sistema RAG")
rag_app = None  # se inicializa en startup

# Diccionario global para mantener las sesiones por user id
chat_sessions = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system when the API starts"""
    global rag_app, chat_sessions

    if rag_app is None:
        load_dotenv()
        rag_app = App()

        # Log the initialized roles
        available_roles = list(rag_app.role_handlers.keys())
        logging.info(f"Initialized handlers for roles: {available_roles}")

@app.post("/query", response_model=Response)
async def process_query(query: Query):
    """Process a query and return response based on role"""
    if not rag_app:
        raise HTTPException(status_code=500, detail="System not initialized")

    try:
        if query.role not in ROLE_PDF_MAPPING:
            raise HTTPException(
                status_code=403,
                detail=f"Invalid role: {query.role}"
            )

        if query.userId in chat_sessions:
            chat_handler = chat_sessions[query.userId]
        else:
            prototype = rag_app.get_chat_handler(query.role)
            chat_handler = rag_app.initialize_chat_handler(prototype.retrieval_system)
            chat_sessions[query.userId] = chat_handler

        # Await the async handle_query
        response_text = await chat_handler.handle_query(query.text, query.userId)
        context = await chat_handler.get_relevant_context(query.text, query.userId)
        return Response(answer=response_text, context=context)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
