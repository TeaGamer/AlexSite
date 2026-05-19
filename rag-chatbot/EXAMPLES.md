# 📝 Приклади використання RAG Chatbot з API

Цей файл містить приклади для різних мов програмування.

## 🐍 Python

### Базовий приклад

```python
import requests
import json

# Конфігурація
BASE_URL = "http://localhost:8000/api/rag"

# 1. Завантажити документ
def upload_document(file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/upload-document", files=files)
    print(response.json())

# 2. Задати питання
def ask_question(question):
    payload = {
        "question": question,
        "session_id": "user_123",
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    return response.json()

# Использование
upload_document("study_program.pdf")
result = ask_question("Які вимоги до вступу?")
print(f"Відповідь: {result['answer']}")
```

### З використанням сесій

```python
import requests
import json

class RAGChatbot:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = "session_123"
    
    def chat(self, question):
        payload = {
            "question": question,
            "session_id": self.session_id,
            "top_k": 3
        }
        response = requests.post(
            f"{self.base_url}/api/rag/chat",
            json=payload
        )
        data = response.json()
        return {
            "answer": data["answer"],
            "sources": data.get("sources", [])
        }
    
    def upload_pdf(self, file_path):
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.base_url}/api/rag/upload-document",
                files=files
            )
        return response.json()
    
    def search(self, query):
        payload = {"query": query, "top_k": 3}
        response = requests.post(
            f"{self.base_url}/api/rag/search",
            json=payload
        )
        return response.json()

# Использование
bot = RAGChatbot()
bot.upload_pdf("study_program.pdf")
result = bot.chat("Які курси є обов'язковими?")
print(result)
```

## 🌐 JavaScript/Node.js

### Базовий приклад

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/rag';

// Завантажити документ
async function uploadDocument(filePath) {
  const FormData = require('form-data');
  const fs = require('fs');
  
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  
  const response = await axios.post(
    `${BASE_URL}/upload-document`,
    form,
    { headers: form.getHeaders() }
  );
  
  return response.data;
}

// Задати питання
async function askQuestion(question) {
  const payload = {
    question: question,
    session_id: 'user_123',
    top_k: 3
  };
  
  const response = await axios.post(`${BASE_URL}/chat`, payload);
  return response.data;
}

// Использование
(async () => {
  await uploadDocument('study_program.pdf');
  const result = await askQuestion('Які вимоги до допуску?');
  console.log('Відповідь:', result.answer);
})();
```

### Клас для зручності

```javascript
class RAGChatbot {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = 'session_' + Date.now();
  }
  
  async chat(question) {
    try {
      const response = await fetch(`${this.baseUrl}/api/rag/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          session_id: this.sessionId,
          top_k: 3
        })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Помилка:', error);
      throw error;
    }
  }
  
  async search(query) {
    const response = await fetch(`${this.baseUrl}/api/rag/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        top_k: 3
      })
    });
    
    return await response.json();
  }
  
  async getDocuments() {
    const response = await fetch(`${this.baseUrl}/api/rag/documents`);
    return await response.json();
  }
}

// Использование
const bot = new RAGChatbot();
bot.chat('Які курси доступні?').then(result => {
  console.log(result.answer);
  console.log('Джерела:', result.sources);
});
```

## 🦀 cURL (Командна строка)

### Завантажити документ

```bash
curl -X POST "http://localhost:8000/api/rag/upload-document" \
  -F "file=@study_program.pdf"
```

### Задати питання

```bash
curl -X POST "http://localhost:8000/api/rag/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Які обов'"'"'язкові курси?",
    "session_id": "user_123",
    "top_k": 3
  }'
```

### Семантичний пошук

```bash
curl -X POST "http://localhost:8000/api/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "курси програмування",
    "top_k": 3
  }'
```

### Список документів

```bash
curl "http://localhost:8000/api/rag/documents"
```

### Видалити документ

```bash
curl -X DELETE "http://localhost:8000/api/rag/documents/doc_id_123"
```

## 🔄 流程приклад (Python)

```python
import requests
import time

class DocumentWorkflow:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.documents = []
    
    def load_dataset(self, csv_file):
        """Завантажити набір даних (CSV/JSON)"""
        with open(csv_file, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.base_url}/api/rag/upload-dataset",
                files=files
            )
        return response.json()
    
    def ask_multiple_questions(self, questions):
        """Задати кілька питань"""
        results = []
        for q in questions:
            time.sleep(0.5)  # Уникнуть rate limiting
            payload = {
                "question": q,
                "session_id": "workflow_123",
                "top_k": 3
            }
            response = requests.post(
                f"{self.base_url}/api/rag/chat",
                json=payload
            )
            results.append(response.json())
        return results
    
    def export_results(self, results, output_file):
        """Експортувати результати"""
        import json
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

# Использование
workflow = DocumentWorkflow()

# 1. Завантажити дані
workflow.load_dataset("programs.csv")

# 2. Задати питання
questions = [
    "Які вимоги до вступу?",
    "Скільки семестрів на програмі?",
    "Які обов'язкові дисципліни?"
]

results = workflow.ask_multiple_questions(questions)

# 3. Зберегти результати
workflow.export_results(results, "answers.json")
```

## ⚙️ Інтеграція з фронтенд (React)

```jsx
import React, { useState } from 'react';

function ChatComponent() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/rag/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          session_id: 'user_123',
          top_k: 3
        })
      });
      
      const data = await response.json();
      
      setMessages(prev => [
        ...prev,
        { user: input, bot: data.answer, sources: data.sources }
      ]);
      setInput('');
    } catch (error) {
      console.error('Помилка:', error);
    }
    
    setLoading(false);
  };
  
  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i}>
            <p className="user-msg">Ви: {msg.user}</p>
            <p className="bot-msg">Бот: {msg.bot}</p>
            {msg.sources && (
              <div className="sources">
                Джерела: {msg.sources.map(s => s.source).join(', ')}
              </div>
            )}
          </div>
        ))}
      </div>
      
      <form onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Введіть питання..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Завантаження...' : 'Надіслати'}
        </button>
      </form>
    </div>
  );
}

export default ChatComponent;
```

## 🛠️ Тестування з Pytest

```python
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestRAGChatbot:
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
    
    def test_config_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "llm_provider" in data
        assert data["llm_provider"] == "openai"
    
    def test_chat_endpoint(self):
        payload = {
            "question": "Тестове питання",
            "session_id": "test_session",
            "top_k": 3
        }
        response = requests.post(f"{BASE_URL}/api/rag/chat", json=payload)
        # Може бути 200 або помилка про порожню БД
        assert response.status_code in [200, 400]
    
    def test_search_endpoint(self):
        payload = {"query": "тест", "top_k": 3}
        response = requests.post(f"{BASE_URL}/api/rag/search", json=payload)
        assert response.status_code in [200, 400]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## 📊 Моніторинг витрат OpenAI

```python
import os
from datetime import datetime, timedelta

# Перевірити лік на https://platform.openai.com/account/billing/overview

def estimate_cost(tokens_used, model="gpt-3.5-turbo"):
    """Оцінити вартість запитів"""
    prices = {
        "gpt-3.5-turbo": {
            "input": 0.0005,  # за 1K токенів
            "output": 0.0015
        },
        "gpt-4": {
            "input": 0.03,
            "output": 0.06
        }
    }
    
    if model in prices:
        price = prices[model]["input"] * (tokens_used / 1000)
        return price
    return None

# Приклад
estimated = estimate_cost(10000, "gpt-3.5-turbo")
print(f"Приблизна вартість: ${estimated:.4f}")
```

## 📚 Додаткові ресурси

- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Swagger UI](http://localhost:8000/docs)
- [API_SETUP.md](API_SETUP.md)

Комбіно успіхів з вашими запитами! 🚀
