from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio

# Завантажимо змінні з .env
load_dotenv()

# Отримаємо API ключ
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY не знайдений у змінних середовища")

# Налаштуємо Google API
genai.configure(api_key=api_key)

# Створимо FastAPI додаток
app = FastAPI(title="Gemini ChatBot API")

# Налаштування CORS
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8000,https://alexsite-swzo.onrender.com').split(',')
cors_origins = [origin.strip() for origin in cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель для запиту
class MessageRequest(BaseModel):
    message: str

# Зберігаємо chat_session глобально
chat_session = None

@app.on_event("startup")
async def startup():
    global chat_session
    model = genai.GenerativeModel("gemini-3.1-flash-lite")
    chat_session = model.start_chat(history=[])

@app.post("/api/chat/stream")
async def chat_stream(request: MessageRequest):
    """Streaming API для чату"""
    global chat_session
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Повідомлення не може бути пустим")
    
    async def generate():
        try:
            response = chat_session.send_message(request.message, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text.encode('utf-8')
                    await asyncio.sleep(0)
        except Exception as e:
            yield f"Помилка: {str(e)}".encode('utf-8')
    
    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")

@app.post("/api/chat")
async def chat(request: MessageRequest):
    """API для чату (звичайна відповідь без потокової передачі)"""
    global chat_session
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Повідомлення не може бути пустим")
    
    try:
        response = chat_session.send_message(request.message)
        return {
            "message": request.message,
            "response": response.text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка AI: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check для Render"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
