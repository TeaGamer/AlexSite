"""PDF and document processing utilities"""
import os
from typing import List, Tuple
from pathlib import Path
import PyPDF2
import uuid
from app.config import settings


def generate_document_id() -> str:
    """Generate unique document ID"""
    return str(uuid.uuid4())


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
                text += f"\n[Page {page_num + 1}]\n"
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")
    return text


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping chunks"""
    if chunk_size is None:
        chunk_size = settings.chunk_size
    if overlap is None:
        overlap = settings.chunk_overlap

    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [c for c in chunks if len(c.strip()) > 0]


def process_uploaded_file(file_path: str, filename: str) -> Tuple[str, List[str]]:
    """
    Process uploaded file and return document ID and chunks
    
    Args:
        file_path: Path to uploaded file
        filename: Original filename
    
    Returns:
        Tuple of (document_id, chunks)
    """
    document_id = generate_document_id()
    
    # Extract text based on file type
    if filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif filename.lower().endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file type: {filename}")
    
    # Chunk the text
    chunks = chunk_text(text)
    
    return document_id, chunks


def save_upload_file(upload_dir: str = "uploads") -> str:
    """Ensure upload directory exists"""
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    return upload_dir


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)


def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
    """
    Validate uploaded file
    
    Args:
        filename: Name of the file
        file_size: Size in bytes
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        return False, f"File size exceeds maximum of {settings.max_upload_size_mb}MB"
    
    allowed_extensions = ['.pdf', '.txt', '.docx']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, ""
