# Study Program RAG Chatbot - LLM + RAG System

Система на базі локальних моделей з Hugging Face (Llama 2) для відповідей на запитання про програми навчання з використанням RAG (Retrieval Augmented Generation).

## Архітектура

```
┌─────────────────────────────────────────────────────┐
│                    User Interface                    │
│                   (Frontend - React)                 │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│          FastAPI Backend (Render Server)            │
├──────────────────────────────────────────────────────┤
│                   RAG Service                       │
│  ┌────────────────────────────────────────────────┐ │
│  │  LLM Service (Llama 2)                         │ │
│  │  • Генерація відповідей                        │ │
│  │  • Обробка контексту                           │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │  Embedding Service (DistilBERT)                │ │
│  │  • Векторизація документів                     │ │
│  │  • Векторизація запитів                        │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │  Vector Store (Chroma)                         │ │
│  │  • Зберігання векторів                         │ │
│  │  • Семантичний пошук                           │ │
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
- PyTorch (з GPU підтримкою опціонально)
- 8GB RAM мінімум (16GB рекомендується для Llama 2)
- GPU опціонально (рекомендується для швидшої роботи)

## Встановлення

### 1. Клонування та підготовка

```bash
cd rag-chatbot
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows
```

### 2. Встановлення залежностей

```bash
pip install -r requirements.txt
```

**Примітка**: Перша інсталяція PyTorch може зайняти час та завантажити великий обсяг даних.

### 3. Налаштування конфігурації

Скопіюйте `.env.example` до `.env` та налаштуйте:

```bash
cp .env.example .env
```

Редагуйте `.env`:

```env
# Модель
LLM_MODEL_NAME=meta-llama/Llama-2-7b-hf
EMBEDDING_MODEL_NAME=sentence-transformers/distilbert-base-uncased

# Пристрій (cpu або cuda)
DEVICE=cpu  # Змініть на cuda, якщо є GPU

# Інші налаштування
VECTOR_DB_TYPE=chroma
CHROMA_PATH=./vector_store
MODELS_CACHE_DIR=./models_cache
```

## Використання

### Запуск сервера

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

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
│   │   ├── llm_service.py     # Llama 2 сервіс
│   │   ├── rag_service.py     # RAG оркестрація
│   │   └── vector_store.py    # Chroma сховище
│   ├── routers/
│   │   └── rag_router.py      # API маршрути
│   └── utils/
│       ├── pdf_processor.py   # Обробка документів
│       ├── dataset_manager.py # Управління датасетами
│       └── fine_tuner.py      # Fine-tuning утиліти
├── uploads/                    # Завантажені файли
├── vector_store/               # Chroma база даних
├── models_cache/               # Кеш завантажених моделей
├── requirements.txt
├── .env.example
└── README.md
```

## Performance Оптимізація

### Для CPU

```env
DEVICE=cpu
MAX_NEW_TOKENS=256
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

### Для GPU (CUDA)

```env
DEVICE=cuda
MAX_NEW_TOKENS=512
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

### 1. Підготовка

- Створіть репозиторій на GitHub
- Добавте файли проекту

### 2. Конфігурація Render

Створіть `render.yaml`:

```yaml
services:
  - type: web
    name: rag-chatbot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: DEVICE
        value: cpu
```

### 3. Деплой

1. Коннектіть GitHub репозиторій до Render
2. Render автоматично деплойятиме на кожен push

## Troubleshooting

### Проблема: "Model not found"
**Рішення**: Переконайтеся, що ім'я моделі правильне. Llama 2 потребує доступ до Hugging Face.

### Проблема: "Out of memory"
**Рішення**: Зменшіть `max_new_tokens` або `chunk_size` в `.env`

### Проблема: Повільна генерація
**Рішення**: Спробуйте меншу модель або GPU

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
