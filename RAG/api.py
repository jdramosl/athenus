from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv
from config.roles import DEFAULT_ROLE, ROLE_PDF_MAPPING
from app import App
from chat.handler import ChatHandler
#import loging
import logging

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
rag_app = None
chat_handler = None

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system when the API starts"""
    global rag_app

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
        # Validate role
        if query.role not in ROLE_PDF_MAPPING:
            raise HTTPException(
                status_code=403,
                detail=f"Invalid role: {query.role}"
            )

        # Get the pre-initialized chat handler for the role
        chat_handler = rag_app.get_chat_handler(query.role)

        if not chat_handler:
            raise HTTPException(
                status_code=403,
                detail=f"No handler available for role: {query.role}"
            )

        # Get relevant context
        context = await chat_handler.get_relevant_context(query.text)

        # Generate response
        response = chat_handler.chain.invoke({
            "context": context,
            "question": query.text
        })

        return Response(answer=response, context=context)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
