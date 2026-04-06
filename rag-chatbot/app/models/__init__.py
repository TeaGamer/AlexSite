"""Pydantic models for API requests and responses"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)  # Number of relevant documents to retrieve


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str
    sources: List[dict] = Field(default_factory=list)
    session_id: str
    timestamp: datetime


class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents"""
    filename: str
    file_size: int
    upload_date: datetime
    document_id: str
    chunks_count: int


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    success: bool
    message: str
    document: Optional[DocumentMetadata] = None


class DocumentListResponse(BaseModel):
    """Response listing all documents"""
    documents: List[DocumentMetadata]
    total_count: int


class SearchQuery(BaseModel):
    """Request for semantic search"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    """Single search result"""
    content: str
    source: str
    relevance_score: float
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response for search endpoint"""
    results: List[SearchResult]
    query: str
    total_results: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    vector_db_type: str
