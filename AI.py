from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import csv
import io
from dotenv import load_dotenv
from google import genai
import asyncio
import shutil
from pathlib import Path

# LangChain imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain.schema import Document

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment")

# Configure Google API
client = genai.Client(api_key=api_key)

# Create FastAPI app
app = FastAPI(title="Gemini ChatBot API with RAG")

# Configure CORS
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',')
cors_origins = [origin.strip() for origin in cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompt — university assistant
SYSTEM_PROMPT = """You are a university assistant chatbot. Your role is to help students and staff with questions about:
- Course listings by field of study and semester
- Subject descriptions and syllabi (learning outcomes, topics covered)
- Exam and credit dates / schedules
- Lecturer information and consultation hours
- Study rules, enrollment requirements, and academic regulations

IMPORTANT RULES:
1. Always respond in the same language the user writes in. Supported languages: Ukrainian (uk), Polish (pl), English (en).
2. Base your answers strictly on the provided context from the university knowledge base.
3. If the answer is not found in the context, say honestly that you don't have that information and suggest the user contact the dean's office.
4. Do not invent or guess information about specific courses, lecturers, or dates.
5. Be concise, friendly, and helpful.
"""

# Request models
class MessageRequest(BaseModel):
    message: str

class URLRequest(BaseModel):
    url: str

# Global variables
chat_session = None
vector_store = None
embeddings = None

# Upload folder for files
UPLOAD_FOLDER = "uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

@app.on_event("startup")
async def startup():
    global chat_session, embeddings, vector_store
    model_name = os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash-lite")
    chat_session = client.chats.create(
        model=model_name,
        config={"system_instruction": SYSTEM_PROMPT}
    )

    # Initialize embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Initialize Chroma vector store
    vector_store = Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

def get_relevant_context(query: str, k: int = 5) -> str:
    """Get relevant context from vector store"""
    global vector_store
    if not vector_store:
        return ""

    try:
        results = vector_store.similarity_search(query, k=k)
        if not results:
            return ""
        context = "\n\n".join([doc.page_content for doc in results])
        return context
    except:
        return ""

def build_prompt(user_message: str, context: str) -> str:
    """Build final prompt with or without RAG context"""
    if context:
        return f"""Use the following university knowledge base to answer the question.
Answer in the same language as the question (Ukrainian, Polish, or English).

--- KNOWLEDGE BASE ---
{context}
--- END OF KNOWLEDGE BASE ---

Question: {user_message}"""
    else:
        return user_message

@app.post("/api/chat/stream")
async def chat_stream(request: MessageRequest):
    """Streaming API for chat with RAG"""
    global chat_session

    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    context = get_relevant_context(request.message)
    enhanced_message = build_prompt(request.message, context)

    async def generate():
        try:
            response = chat_session.send_message_stream(enhanced_message)
            for chunk in response:
                if chunk.text:
                    yield chunk.text.encode('utf-8')
                    await asyncio.sleep(0)
        except Exception as e:
            yield f"Error: {str(e)}".encode('utf-8')

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")

@app.post("/api/chat")
async def chat(request: MessageRequest):
    """API for chat (normal response without streaming) with RAG"""
    global chat_session

    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        context = get_relevant_context(request.message)
        enhanced_message = build_prompt(request.message, context)

        response = chat_session.send_message(enhanced_message)
        return {
            "message": request.message,
            "response": response.text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

@app.post("/api/documents/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF file and add to knowledge base"""
    global vector_store

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        safe_filename = Path(file.filename).name
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        docs = text_splitter.split_documents(documents)

        vector_store.add_documents(docs)

        return {
            "status": "success",
            "filename": file.filename,
            "documents_added": len(docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")

@app.post("/api/documents/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file and add to knowledge base.

    Each row is converted to a readable text chunk so the AI can answer
    questions about courses, lecturers, schedules, etc.

    Expected CSV columns (flexible — any columns are accepted):
      e.g. subject, lecturer, semester, field, description, consultations, exam_date ...
    """
    global vector_store

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        content = await file.read()
        decoded = content.decode('utf-8-sig')  # handle BOM from Excel
        reader = csv.DictReader(io.StringIO(decoded))

        docs = []
        for i, row in enumerate(reader):
            # Build human-readable text from all columns
            row_text = "\n".join(
                f"{key.strip()}: {value.strip()}"
                for key, value in row.items()
                if value and value.strip()
            )
            if row_text:
                docs.append(Document(
                    page_content=row_text,
                    metadata={"source": file.filename, "row": i + 1}
                ))

        if not docs:
            raise HTTPException(status_code=400, detail="CSV file is empty or has no valid rows")

        # Split long rows if needed
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
        )
        split_docs = text_splitter.split_documents(docs)

        vector_store.add_documents(split_docs)

        return {
            "status": "success",
            "filename": file.filename,
            "rows_processed": len(docs),
            "documents_added": len(split_docs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading CSV: {str(e)}")

@app.post("/api/documents/upload-url")
async def upload_url(request: URLRequest):
    """Upload content from URL (HTML page) and add to knowledge base"""
    global vector_store

    try:
        loader = WebBaseLoader(request.url)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        docs = text_splitter.split_documents(documents)

        vector_store.add_documents(docs)

        return {
            "status": "success",
            "url": request.url,
            "documents_added": len(docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading URL: {str(e)}")

@app.get("/api/documents/count")
async def get_documents_count():
    """Get document count in vector database"""
    global vector_store
    try:
        count = vector_store._collection.count()
        return {"documents_count": count}
    except:
        return {"documents_count": 0}

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "ok"}

def console_chat():
    """Simple console chat for testing"""
    print("Initializing model...")
    model_name = os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash-lite")
    session = client.chats.create(
        model=model_name,
        config={"system_instruction": SYSTEM_PROMPT}
    )
    emb = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vs = Chroma(
        collection_name="documents",
        embedding_function=emb,
        persist_directory="./chroma_db"
    )
    print("Console chat ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        try:
            results = vs.similarity_search(user_input, k=5)
            context = "\n\n".join([doc.page_content for doc in results])
        except Exception:
            context = ""
        prompt = build_prompt(user_input, context)
        try:
            response = session.send_message(prompt)
            print(f"Bot: {response.text}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    import sys
    if "--console" in sys.argv:
        console_chat()
    else:
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)
