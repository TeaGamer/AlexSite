"""RAG (Retrieval Augmented Generation) service"""
from typing import List, Tuple, Optional
from app.services.llm_service import get_llm_service, get_embedding_service
from app.services.vector_store import get_vector_store
from app.utils.pdf_processor import chunk_text
import uuid
from datetime import datetime


class RAGService:
    """Service for Retrieval Augmented Generation"""
    
    def __init__(self):
        """Initialize RAG service"""
        self.llm_service = get_llm_service()
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.documents_metadata = {}  # Track document metadata
    
    def add_documents(
        self,
        texts: List[str],
        source: str = "unknown",
        metadata: dict = None
    ) -> str:
        """
        Add documents to the RAG system
        
        Args:
            texts: List of text chunks or documents
            source: Source of the documents
            metadata: Additional metadata
        
        Returns:
            Document ID
        """
        document_id = str(uuid.uuid4())
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "source": source,
            "added_date": datetime.now().isoformat(),
            "document_id": document_id
        })
        
        # Chunk and embed texts
        all_chunks = []
        for text in texts:
            if isinstance(text, str):
                chunks = chunk_text(text)
                all_chunks.extend(chunks)
        
        if not all_chunks:
            raise ValueError("No valid chunks to add")
        
        print(f"Processing {len(all_chunks)} chunks...")
        
        # Generate embeddings
        embeddings = self.embedding_service.get_embeddings_batch(all_chunks)
        
        # Add to vector store
        self.vector_store.add_documents(
            chunks=all_chunks,
            document_id=document_id,
            embeddings=embeddings,
            metadata=metadata
        )
        
        # Store metadata
        self.documents_metadata[document_id] = {
            **metadata,
            "chunks_count": len(all_chunks),
            "texts_count": len(texts)
        }
        
        print(f"Document {document_id} added successfully!")
        return document_id
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        system_prompt: str = None
    ) -> Tuple[str, List[dict]]:
        """
        Query the RAG system
        
        Args:
            question: User's question
            top_k: Number of relevant documents to retrieve
            system_prompt: Optional custom system prompt
        
        Returns:
            Tuple of (answer, sources)
        """
        # Get query embedding
        query_embedding = self.embedding_service.get_embedding(question)
        
        # Search vector store
        search_results = self.vector_store.search(query_embedding, top_k=top_k)
        
        if not search_results:
            return "No relevant documents found in the knowledge base.", []
        
        # Build context from search results
        context_parts = []
        sources = []
        
        for content, similarity, metadata in search_results:
            context_parts.append(content)
            sources.append({
                "content": content[:500],  # First 500 chars
                "similarity": float(similarity),
                "source": metadata.get("source", "unknown"),
                "document_id": metadata.get("document_id", "unknown")
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate response using LLM
        answer = self.llm_service.generate_response(
            question=question,
            context=context,
            system_prompt=system_prompt
        )
        
        return answer, sources
    
    def query_with_reranking(
        self,
        question: str,
        top_k: int = 10,
        rerank_top_k: int = 5,
        system_prompt: str = None
    ) -> Tuple[str, List[dict]]:
        """
        Query with re-ranking (retrieve more, then select best)
        
        Args:
            question: User's question
            top_k: Initial number of results to retrieve
            rerank_top_k: Number of results to use after re-ranking
            system_prompt: Optional custom system prompt
        
        Returns:
            Tuple of (answer, sources)
        """
        # Get query embedding
        query_embedding = self.embedding_service.get_embedding(question)
        
        # Get initial results
        search_results = self.vector_store.search(query_embedding, top_k=top_k)
        
        if not search_results:
            return "No relevant documents found. Please check your knowledge base.", []
        
        # Re-rank and select top results
        sorted_results = sorted(search_results, key=lambda x: x[1], reverse=True)
        selected_results = sorted_results[:rerank_top_k]
        
        # Build context
        context_parts = []
        sources = []
        
        for content, similarity, metadata in selected_results:
            context_parts.append(content)
            sources.append({
                "content": content[:500],
                "similarity": float(similarity),
                "source": metadata.get("source", "unknown"),
                "document_id": metadata.get("document_id", "unknown")
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate response
        answer = self.llm_service.generate_response(
            question=question,
            context=context,
            system_prompt=system_prompt
        )
        
        return answer, sources
    
    def delete_document(self, document_id: str):
        """Delete a document from the system"""
        self.vector_store.delete_document(document_id)
        if document_id in self.documents_metadata:
            del self.documents_metadata[document_id]
    
    def get_documents_info(self) -> List[dict]:
        """Get information about all stored documents"""
        return list(self.documents_metadata.values())
    
    def add_from_dataset(
        self,
        dataset: List[dict],
        text_column: str = "content",
        source_column: str = "source",
        metadata_fields: List[str] = None
    ) -> List[str]:
        """
        Add multiple documents from a dataset
        
        Args:
            dataset: List of dictionaries representing documents
            text_column: Column name containing text
            source_column: Column name containing source info
            metadata_fields: Additional fields to store as metadata
        
        Returns:
            List of document IDs
        """
        document_ids = []
        
        for item in dataset:
            if text_column not in item:
                continue
            
            text = item[text_column]
            source = item.get(source_column, "dataset")
            
            metadata = {}
            if metadata_fields:
                for field in metadata_fields:
                    if field in item:
                        metadata[field] = str(item[field])
            
            try:
                doc_id = self.add_documents(
                    texts=[text],
                    source=source,
                    metadata=metadata
                )
                document_ids.append(doc_id)
            except Exception as e:
                print(f"Error processing document: {str(e)}")
        
        return document_ids


# Global instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
