# Study Program RAG Chatbot - API-Based LLM + RAG System

Система на базі **зовнішніх LLM API** (OpenAI, Anthropic, Cohere) з **локальною RAG системою** для відповідей на запитання про програми навчання.

## 🎯 Що нове?

- ✅ **Не потрібно завантажувати локальні моделі** (економія 5GB+ диску)
- ✅ **Використання найновіших моделей** (GPT-4, Claude, тощо)
- ✅ **Краща якість відповідей**
- ✅ **Вибір провайдера** (OpenAI, Anthropic, Cohere)
- ✅ **Система RAG залишилась локальною** (приватні embeddings)

## Архітектура

```
┌─────────────────────────────────────────────────────┐
│                    User Interface                    │
│                   (Frontend - React)                 │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│          FastAPI Backend (Your Server)              │
├──────────────────────────────────────────────────────┤
│                   RAG Service                       │
│  ┌────────────────────────────────────────────────┐ │
│  │  LLM Service (OpenAI/Anthropic/Cohere API) ☁️  │ │
│  │  • Генерація відповідей через API             │ │
│  │  • Обробка контексту                          │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │  Embedding Service (DistilBERT) 💻             │ │
│  │  • Локальна векторизація документів            │ │
│  │  • Локальна векторизація запитів              │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │  Vector Store (Chroma) 📊                      │ │
│  │  • Зберігання векторів локально                │ │
│  │  • Семантичний пошук                          │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Knowledge Base                         │
│  • CSV/JSON датасети                                │
│  • PDF документи                                    │
│  • Текстові файли                                   │
└──────────────────────────────────────────────────────┘
```

## Вимоги

- Python 3.10+
- API ключ від (OpenAI / Anthropic / Cohere)
- 2GB RAM мінімум (для embeddings)
- Інтернет з'єднання

## ⚡ Швидкий старт

**Рекомендуємо прочитати [QUICKSTART_API.md](QUICKSTART_API.md) для швидкого налаштування!**

### 1. Встановлення

Сервер запуститься на `http://localhost:8000`

### API Endpoints

#### 1. **Health Check**
```bash
GET /health
```

#### 2. **Chat (основне запитання)**
```bash
POST /api/rag/chat
Content-Type: application/json

{
  "question": "Які курси потрібні на першому році?",
  "top_k": 5,
  "session_id": "user123"
}
```

Відповідь:
```json
{
  "answer": "Перший курс включає...",
  "sources": [
    {
      "content": "...",
      "similarity": 0.95,
      "source": "study_program.pdf"
    }
  ],
  "session_id": "user123",
  "timestamp": "2024-01-15T10:30:00"
}
```

#### 3. **Семантичний пошук**
```bash
POST /api/rag/search
Content-Type: application/json

{
  "query": "вимоги до випускової роботи",
  "top_k": 5
}
```

#### 4. **Завантаження документа**
```bash
POST /api/rag/upload-document
Form-data:
  - file: study_program.pdf
  - source_name: "Study Program 2024"
```

#### 5. **Завантаження датасету**
```bash
POST /api/rag/upload-dataset
Form-data:
  - file: courses.csv
  - text_column: "description"
  - source_column: "course_name"
```

Очікуваний формат CSV:
```csv
course_name,description,credits
Math 101,Basic mathematics,3
Programming 101,Introduction to programming,4
```

#### 6. **Список документів**
```bash
GET /api/rag/documents
```

#### 7. **Видалення документа**
```bash
DELETE /api/rag/documents/{document_id}
```

## Робота з датасетами

### Приклад CSV датасету

```csv
title,content,source
Course Requirements,All students must complete...,Program Handbook
Graduation Requirements,Students need 120 credits...,Academic Calendar
Course Schedule,Spring semester includes...,Course Catalog
```

### Приклад JSON датасету

```json
[
  {
    "title": "Course Requirements",
    "content": "All students must complete the core curriculum...",
    "source": "handbook.pdf"
  },
  {
    "title": "Graduation Requirements",
    "content": "Students need 120 credits to graduate...",
    "source": "academic_calendar.pdf"
  }
]
```

### Завантаження датасету

```python
import requests

with open('courses.csv', 'rb') as f:
    files = {'file': f}
    data = {
        'text_column': 'content',
        'source_column': 'source'
    }
    response = requests.post(
        'http://localhost:8000/api/rag/upload-dataset',
        files=files,
        data=data
    )
```

## Fine-tuning моделі

### 1. Підготовка даних

```python
from app.utils.fine_tuner import FineTuner

training_data = [
    {
        "question": "Які вимоги для вступу?",
        "answer": "Вимоги включають середній бал, тести тощо..."
    },
    {
        "question": "Як довго студіювати?",
        "answer": "Типова програма займає 4 роки..."
    }
]

fine_tuner = FineTuner()
fine_tuner.prepare_training_data(
    data=training_data,
    output_file="training_data.txt"
)
```

### 2. Fine-tuning

```python
fine_tuner.fine_tune(
    training_file="training_data.txt",
    output_dir="./fine_tuned_model",
    num_epochs=3,
    batch_size=4,
    learning_rate=2e-5
)
```

### 3. Використання fine-tuned моделі

Оновіть `.env`:
```env
LLM_MODEL_NAME=./fine_tuned_model
```

Перезапустіть сервер.

## Структура проекту

```
rag-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI додаток
│   ├── config.py               # Конфігурація
│   ├── models/
│   │   └── __init__.py        # Pydantic моделі
│   ├── services/
│   │   ├── llm_service.py     # LLM API сервіс
│   │   ├── rag_service.py     # RAG оркестрація
│   │   └── vector_store.py    # Chroma сховище
│   ├── routers/
│   │   └── rag_router.py      # API маршрути
│   └── utils/
│       ├── pdf_processor.py   # Обробка документів
│       └── dataset_manager.py # Управління датасетами
├── uploads/                    # Завантажені файли
├── vector_store/               # Chroma база даних
├── requirements.txt
├── .env.example
└── README.md
```

## API Провайдери

### OpenAI (Рекомендується)

```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-your-api-key
LLM_MODEL_NAME=gpt-3.5-turbo
```

### Anthropic (Claude)

```env
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-your-api-key
LLM_MODEL_NAME=claude-3-sonnet-20240229
```

### Cohere

```env
LLM_PROVIDER=cohere
LLM_API_KEY=your-cohere-key
LLM_MODEL_NAME=command
```

## Development на локальній машині

### 1. Запуск з релоадом

```bash
python -m uvicorn app.main:app --reload
```

### 2. Тестування endpoints

```python
import requests

# Chat
response = requests.post(
    'http://localhost:8000/api/rag/chat',
    json={'question': 'Які вимоги?'}
)
print(response.json())
```

## Deployment на Render

Детальна інструкція в [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

Швидко:
1. Коннектіть GitHub репозиторій до Render
2. Встановіть environment змінні (особливо `LLM_API_KEY` як secret)
3. Render автоматично деплойятиме на кожен push

## Troubleshooting

### Проблема: "No API key provided"
**Рішення**: Переконайтеся, що `LLM_API_KEY` встановлено в `.env` файлі

### Проблема: "401 Unauthorized"
**Рішення**: API ключ неправильний або закінчився кредит на провайдері

### Проблема: "Rate limit exceeded"
**Рішення**: Чекайте кілька секунд перед наступним запитом

### Проблема: "openai package not installed"
**Рішення**: Запустіть `pip install openai` або `pip install --upgrade -r requirements.txt`

## Дорожна карта

- [ ] WebSocket підтримка для streaming відповідей
- [ ] Multi-language підтримка
- [ ] Históрія діалогів в БД
- [ ] Admin панель для управління документами
- [ ] Advanced RAG (hyde, query expansion)
- [ ] Метрики якості відповідей

## Ліцензія

MIT

## Контакт

Для запитань та пропозицій скористайтеся Issues на GitHub.
