from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv

from app import App
from chat.handler import ChatHandler
from config.roles import DEFAULT_ROLE

# Modelos Pydantic
class Query(BaseModel):
    text: str
    role: str = DEFAULT_ROLE
    feedback: Optional[int] = None

class Response(BaseModel):
    answer: str
    context: str

# Inicializar FastAPI
app = FastAPI(title="RAG API", description="API para el sistema RAG")

# Inicializar el sistema RAG
rag_app = App()
chat_handler = None

@app.on_event("startup")
async def startup_event():
    """Inicializa el sistema RAG cuando arranca la API"""
    global rag_app
    load_dotenv()

    # Initialize the RAG application
    rag_app = App()

@app.post("/query", response_model=Response)
async def process_query(query: Query):
    """Procesa una consulta y devuelve la respuesta basada en el rol"""
    if not rag_app:
        raise HTTPException(status_code=500, detail="El sistema no está inicializado")

    try:
        # Get the appropriate chat handler for the role
        chat_handler = rag_app.get_or_create_role_loader(query.role)

        # Obtener contexto relevante
        context = await chat_handler.get_relevant_context(query.text)

        # Generar respuesta
        response = chat_handler.chain.invoke({
            "context": context,
            "question": query.text
        })

        # Guardar feedback si se proporciona
        if query.feedback is not None:
            chat_handler.save_feedback(query.text, response, query.feedback)

        return Response(answer=response, context=context)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
