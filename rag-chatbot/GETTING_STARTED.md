# Getting Started - RAG Chatbot

Простий гайд для швидкого запуску.

## ⚙️ Вимоги

- Python 3.10+
- 8GB RAM мінімум
- 5GB disk space (для моделей)

## 🚀 Швидкий Старт (5 хвилин)

### 1. Встановлення

```bash
# Клонування
cd rag-chatbot

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows

# Залежності
pip install -r requirements.txt
```

### 2. Налаштування

```bash
# Скопіюйте конфіг
cp .env.example .env

# Редагуйте .env (опціонально)
# За умовчанням все налаштовано для CPU
```

### 3. Запуск

```bash
# Сервер розпочнеться на http://localhost:8000
python -m uvicorn app.main:app --reload
```

### 4. Тестування

Відкрийте нову термінал:

```bash
# Завантаження demo даних
python quickstart.py --setup-data

# Тестування RAG
python quickstart.py --test

# або через API
python test_api.py
```

## 📚 Використання API

### Chat з контекстом

```bash
curl -X POST http://localhost:8000/api/rag/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Які вимоги для випуску?",
    "top_k": 5
  }'
```

### Пошук документів

```bash
curl -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "обов
язкові курси",
    "top_k": 3
  }'
```

### Завантаження CSV

```bash
curl -X POST http://localhost:8000/api/rag/upload-dataset \
  -F "file=@courses.csv" \
  -F "text_column=description" \
  -F "source_column=course_name"
```

## 📖 Приклади

### Python

```python
import requests

# Chat
response = requests.post(
    'http://localhost:8000/api/rag/chat',
    json={
        'question': 'Які курси обов\'язкові?',
        'top_k': 5
    }
)

print(response.json()['answer'])
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/rag/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'Які вимоги?',
    top_k: 5
  })
});

const data = await response.json();
console.log(data.answer);
```

## 📊 Панель

Доступні інтерфейси:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Config**: http://localhost:8000/api/config

## 📁 Структура Данных

### Датасет CSV

```csv
title,content,source
Course 101,Description...,Program Guide
Requirement,Text...,Handbook
```

### Датасет JSON

```json
[
  {
    "title": "Course 101",
    "content": "Description...",
    "source": "Program Guide"
  }
]
```

## 🔧 Конфігурація

Редагуйте `.env` для налаштування:

```env
# Моделі (Hugging Face)
LLM_MODEL_NAME=meta-llama/Llama-2-7b-hf
EMBEDDING_MODEL_NAME=sentence-transformers/distilbert-base-uncased

# Пристрій
DEVICE=cpu  # або cuda

# Параметри
MAX_NEW_TOKENS=512
TEMPERATURE=0.7
```

## 🐛 Проблемы

### "Model loading failed"
```
Рішення: Перша загрузка займає 5-10 хвилин. Чекайте...
```

### "Out of memory"
```
Рішення: Зменшіть MAX_NEW_TOKENS=256 або використовуйте меншу модель
```

### "Slow responses"
```
Рішення: Спробуйте GPU (DEVICE=cuda) або меншу модель
```

## 📚 Далі

- **Fine-tuning**: див. README.md
- **Deployment**: див. DEPLOY_RENDER.md
- **Advanced**: див. документацію

## 💡 Корисні команди

```bash
# Перевірити конфіг
curl http://localhost:8000/api/config

# Список документів
curl http://localhost:8000/api/rag/documents

# Документація JSON
curl http://localhost:8000/openapi.json | python -m json.tool

# Видалити вектор БД (очистити)
rm -rf vector_store/

# Видалити кеш моделей
rm -rf models_cache/
```

## 🌐 Frontend Integration

Приклад для React:

```jsx
const [answer, setAnswer] = useState('');

const askQuestion = async (question) => {
  const res = await fetch('http://localhost:8000/api/rag/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: 5 })
  });
  
  const data = await res.json();
  setAnswer(data.answer);
};
```

## ✅ Перевірка

Запустіть всі тести:

```bash
python test_api.py
```

Очікуваний результат:
```
All tests passed! ✓
```

---

Готово! 🎉 Тепер ви можете використовувати RAG Chatbot.
