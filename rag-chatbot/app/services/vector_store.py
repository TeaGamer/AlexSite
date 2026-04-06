"""Vector store service for managing embeddings and document retrieval"""
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
import chromadb
from chromadb.config import Settings as ChromaSettings
import os
from app.config import settings


class VectorStore(ABC):
    """Abstract base class for vector stores"""
    
    @abstractmethod
    def add_documents(self, chunks: List[str], document_id: str, embeddings: List[List[float]], metadata: dict = None):
        """Add documents to vector store"""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float, dict]]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: str):
        """Delete a document from the store"""
        pass
    
    @abstractmethod
    def get_all_documents(self) -> List[dict]:
        """Get all documents metadata"""
        pass


class ChromaVectorStore(VectorStore):
    """Chroma vector store implementation"""
    
    def __init__(self, path: str = None):
        """Initialize Chroma client"""
        if path is None:
            path = settings.chroma_path
        
        os.makedirs(path, exist_ok=True)
        chroma_settings = ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=path,
            anonymized_telemetry=False,
        )
        self.client = chromadb.Client(chroma_settings)
        self.collection = self.client.get_or_create_collection(
            name="study_program_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self, 
        chunks: List[str], 
        document_id: str, 
        embeddings: List[List[float]], 
        metadata: dict = None
    ):
        """Add document chunks to Chroma"""
        if metadata is None:
            metadata = {}
        
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                **metadata,
                "document_id": document_id,
                "chunk_index": i
            } 
            for i in range(len(chunks))
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float, dict]]:
        """Search in Chroma collection"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results["documents"] or not results["documents"][0]:
                return []
            
            # Convert distances to similarity scores (cosine distance to similarity)
            search_results = []
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similarity = 1 - distance  # Convert distance to similarity
                search_results.append((doc, similarity, metadata))
            
            return search_results
        except Exception as e:
            print(f"Error searching in Chroma: {str(e)}")
            return []
    
    def delete_document(self, document_id: str):
        """Delete all chunks of a document"""
        try:
            # Get all IDs with this document_id
            where_filter = {"document_id": {"$eq": document_id}}
            results = self.collection.get(where=where_filter)
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
        except Exception as e:
            print(f"Error deleting document from Chroma: {str(e)}")
    
    def get_all_documents(self) -> List[dict]:
        """Get metadata of all documents"""
        try:
            results = self.collection.get(include=["metadatas"])
            # Get unique documents
            docs_dict = {}
            for metadata in results["metadatas"]:
                doc_id = metadata.get("document_id")
                if doc_id and doc_id not in docs_dict:
                    docs_dict[doc_id] = metadata
            return list(docs_dict.values())
        except Exception as e:
            print(f"Error getting documents from Chroma: {str(e)}")
            return []


def get_vector_store() -> VectorStore:
    """Factory function to get the configured vector store"""
    return ChromaVectorStore()
