"""RAG Chat API endpoints"""
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from datetime import datetime
import shutil

from app.models import (
    ChatRequest,
    ChatResponse,
    SearchQuery,
    SearchResponse,
    SearchResult,
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentMetadata
)
from app.services.rag_service import get_rag_service
from app.utils.pdf_processor import (
    process_uploaded_file,
    validate_file,
    get_file_size,
    save_upload_file
)
from app.utils.dataset_manager import DatasetManager
from app.config import settings

router = APIRouter(prefix="/api/rag", tags=["RAG"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the RAG system
    
    Query the LLM with context retrieved from the knowledge base
    """
    try:
        rag_service = get_rag_service()
        answer, sources = rag_service.query(
            question=request.question,
            top_k=request.top_k
        )
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=request.session_id or "default",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery):
    """
    Semantic search in the knowledge base
    
    Search for relevant documents without generating a response
    """
    try:
        rag_service = get_rag_service()
        embedding_service = rag_service.embedding_service
        vector_store = rag_service.vector_store
        
        # Get query embedding
        query_embedding = embedding_service.get_embedding(query.query)
        
        # Search
        search_results = vector_store.search(query_embedding, top_k=query.top_k)
        
        results = []
        for content, similarity, metadata in search_results:
            results.append(SearchResult(
                content=content,
                source=metadata.get("source", "unknown"),
                relevance_score=float(similarity),
                metadata=metadata
            ))
        
        return SearchResponse(
            results=results,
            query=query.query,
            total_results=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    source_name: Optional[str] = None
):
    """
    Upload and process a document
    
    Supports PDF and TXT files
    """
    try:
        # Validate file
        file_size = await file.read()
        await file.seek(0)
        is_valid, error_msg = validate_file(file.filename, len(file_size))
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Save uploaded file
        upload_dir = save_upload_file(settings.model_dump().get("dataset_path", "uploads"))
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            f.write(file_size)
        
        # Process file
        document_id, chunks = process_uploaded_file(file_path, file.filename)
        
        # Add to RAG
        rag_service = get_rag_service()
        rag_service.add_documents(
            texts=chunks,
            source=source_name or file.filename,
            metadata={
                "filename": file.filename,
                "file_size": len(file_size)
            }
        )
        
        # Return response
        doc_metadata = DocumentMetadata(
            filename=file.filename,
            file_size=len(file_size),
            upload_date=datetime.now(),
            document_id=document_id,
            chunks_count=len(chunks)
        )
        
        return DocumentUploadResponse(
            success=True,
            message=f"Document uploaded successfully. {len(chunks)} chunks created.",
            document=doc_metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    text_column: str = "content",
    source_column: str = "source"
):
    """
    Upload a CSV or JSON dataset
    
    Expected format: List of dictionaries with text and source columns
    """
    try:
        # Save file
        upload_dir = save_upload_file(settings.model_dump().get("dataset_path", "uploads"))
        file_path = os.path.join(upload_dir, file.filename)
        
        file_content = await file.read()
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Load dataset
        dataset_manager = DatasetManager()
        
        if file.filename.endswith('.csv'):
            df = dataset_manager.load_csv(file_path)
            data = df.to_dict('records')
        elif file.filename.endswith('.json'):
            data = dataset_manager.load_json(file_path)
        elif file.filename.endswith('.jsonl'):
            data = dataset_manager.load_jsonl(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Validate
        is_valid, errors = dataset_manager.validate_dataset(data, [text_column, source_column])
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Dataset validation errors: {errors}")
        
        # Add to RAG
        rag_service = get_rag_service()
        document_ids = rag_service.add_from_dataset(
            dataset=data,
            text_column=text_column,
            source_column=source_column
        )
        
        return {
            "success": True,
            "message": f"Dataset uploaded successfully. {len(document_ids)} documents added.",
            "document_ids": document_ids,
            "total_documents": len(data)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def get_documents():
    """Get information about all stored documents"""
    try:
        rag_service = get_rag_service()
        docs = rag_service.get_documents_info()
        
        documents = [
            DocumentMetadata(
                filename=doc.get("source", "unknown"),
                file_size=doc.get("file_size", 0),
                upload_date=datetime.fromisoformat(doc.get("added_date", datetime.now().isoformat())),
                document_id=doc.get("document_id", "unknown"),
                chunks_count=doc.get("chunks_count", 0)
            )
            for doc in docs
        ]
        
        return DocumentListResponse(
            documents=documents,
            total_count=len(documents)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base"""
    try:
        rag_service = get_rag_service()
        rag_service.delete_document(document_id)
        
        return {
            "success": True,
            "message": f"Document {document_id} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
