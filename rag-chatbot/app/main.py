"""Main FastAPI application"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.config import settings
from app.routers.rag_router import router as rag_router
from app.models import HealthResponse

# Create FastAPI app
app = FastAPI(
    title="Study Program RAG Chatbot",
    description="LLM-powered RAG system for study program queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(rag_router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        vector_db_type=settings.vector_db_type
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Study Program RAG Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/rag/chat",
            "search": "/api/rag/search",
            "upload_document": "/api/rag/upload-document",
            "upload_dataset": "/api/rag/upload-dataset",
            "documents": "/api/rag/documents",
            "delete_document": "/api/rag/documents/{document_id}",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/api/config")
async def get_config():
    """Get current configuration (non-sensitive info)"""
    return {
        "llm_model": settings.llm_model_name,
        "embedding_model": settings.embedding_model_name,
        "device": settings.device,
        "vector_db_type": settings.vector_db_type,
        "environment": settings.environment
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
