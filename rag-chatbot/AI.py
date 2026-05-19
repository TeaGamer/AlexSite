from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Завантажимо змінні з .env
load_dotenv()

# Отримаємо API ключ
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY не знайдений у змінних середовища")

# Налаштуємо Google API
genai.configure(api_key=api_key)

# Створимо FastAPI додаток
app = FastAPI(title="Gemini ChatBot")

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

@app.get("/", response_class=HTMLResponse)
async def get_chat_page():
    """Повертаємо HTML сторінку"""
    return """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 Gemini ChatBot</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                width: 100%;
                max-width: 800px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                display: flex;
                flex-direction: column;
                height: 90vh;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 15px 15px 0 0;
                text-align: center;
            }
            
            .header h1 {
                font-size: 24px;
                margin-bottom: 5px;
            }
            
            .chat-box {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .user-message {
                justify-content: flex-end;
            }
            
            .user-message .msg-content {
                background: #667eea;
                color: white;
                padding: 12px 16px;
                border-radius: 15px;
                max-width: 70%;
                word-wrap: break-word;
            }
            
            .bot-message .msg-content {
                background: #e9ecef;
                color: #333;
                padding: 12px 16px;
                border-radius: 15px;
                max-width: 70%;
                word-wrap: break-word;
            }
            
            .input-area {
                display: flex;
                gap: 10px;
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
                border-radius: 0 0 15px 15px;
            }
            
            .input-area input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 25px;
                font-size: 14px;
                outline: none;
                transition: border 0.3s;
            }
            
            .input-area input:focus {
                border-color: #667eea;
            }
            
            .input-area button {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.3s;
            }
            
            .input-area button:hover {
                background: #764ba2;
            }
            
            .input-area button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .loading {
                display: inline-block;
                width: 8px;
                height: 8px;
                background: #667eea;
                border-radius: 50%;
                animation: loading 1.4s infinite;
            }
            
            @keyframes loading {
                0%, 100% { opacity: 0.3; }
                50% { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Gemini ChatBot</h1>
                <p>Запитайте мене про що-небудь!</p>
            </div>
            <div class="chat-box" id="chatBox"></div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Напишіть повідомлення..." />
                <button id="sendBtn" onclick="sendMessage()">Надіслати</button>
            </div>
        </div>

        <script>
            const chatBox = document.getElementById('chatBox');
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');

            function addMessage(text, isUser) {
                const msgDiv = document.createElement('div');
                msgDiv.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
                msgDiv.innerHTML = '<div class="msg-content">' + escapeHtml(text) + '</div>';
                chatBox.appendChild(msgDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            function escapeHtml(text) {
                const map = {
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#039;'
                };
                return text.replace(/[&<>"']/g, m => map[m]);
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                addMessage(message, true);
                messageInput.value = '';
                sendBtn.disabled = true;

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });

                    if (!response.ok) {
                        throw new Error('Помилка сервера');
                    }

                    const data = await response.json();
                    addMessage(data.reply, false);
                } catch (error) {
                    addMessage('❌ Помилка: ' + error.message, false);
                } finally {
                    sendBtn.disabled = false;
                    messageInput.focus();
                }
            }

            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            // Приветствие
            addMessage('Привіт! 👋 Я Gemini ChatBot. Чим я можу вам допомогти?', false);
            messageInput.focus();
        </script>
    </body>
    </html>
    """

@app.post("/api/chat")
async def chat(request: MessageRequest):
    """API для чату"""
    global chat_session
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Повідомлення не може бути пустим")
    
    try:
        response = chat_session.send_message(request.message, stream=True)
        full_response = ""
        for chunk in response:
            full_response += chunk.text
        return {"reply": full_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check для Render"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
