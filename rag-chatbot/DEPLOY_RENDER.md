# Deployment Guide - Render

Цей гайд описує як розгорнути RAG Chatbot на Render servidor.

## Підготовка до деплою

### 1. GitHub Repository

Переконайтеся, що ваш репозиторій налаштований правильно:

```bash
git init
git add .
git commit -m "Initial RAG chatbot setup"
git push origin main
```

### 2. Render Account

1. Зареєструйтеся на [render.com](https://render.com)
2. Коннектіть GitHub акаунт
3. Виберіть репозиторій

## Deployment Process

### Вручну через Web Console

1. На Render dashboard, натисніть "New+" → "Web Service"
2. Виберіть GitHub репозиторій
3. Налаштуйте наступні параметри:

**Basic Settings:**
- Name: `study-program-rag-chatbot`
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Environment Variables:**
- `PYTHON_VERSION`: `3.10.0`
- `LLM_PROVIDER`: `openai` (або `anthropic`, `cohere`)
- `LLM_API_KEY`: `sk-proj-your-api-key` (отримайте з провайдера)
- `LLM_MODEL_NAME`: `gpt-3.5-turbo` (або `gpt-4`, `claude-3-sonnet`)
- `EMBEDDING_MODEL_NAME`: `sentence-transformers/distilbert-base-uncased`
- `DEVICE`: `cpu`
- `PYTHONUNBUFFERED`: `1`

### Через render.yaml

Render.yaml вже налаштований. Просто виконайте:

```bash
git push origin main
```

## Оптимізація для Render

### 1. API Key Security

Переконайтеся, що API ключ встановлено як secret variable на Render:

```env
LLM_API_KEY=sk-proj-your-actual-key
```

⚠️ **НЕ** додавайте ключ до `.env` файлу в гіті!

### 2. Startup Time

Запуск буде миттєвим (30 сек - 1 хвилина):

- Немає завантаження моделей
- API клієнт ініціалізується швидко
- Слідкуйте за логами в Render dashboard

### 3. Персистентне сховище

На Render, дані в `/app` втрачаються при перезавантаженні. Альтернативи:

**Опція 1: PostgreSQL для зберігання метаданих**
```python
# app/utils/persistence.py
import psycopg2

db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
```

**Опція 2: Redis для кешування**
```bash
# На Render, додайте Redis service
redis-url = os.getenv("REDIS_URL")
```

**Опція 3: S3/Backup периодично**
```bash
# Бекап vector store в облако щоночі
```

## Перевірка Deployment

### Health Check

```bash
curl https://your-app.onrender.com/health
```

Очікуваний результат:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_db_type": "chroma"
}
```

### Тестування API

```bash
curl -X POST https://your-app.onrender.com/api/rag/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are graduation requirements?",
    "top_k": 5
  }'
```

## Логи

Переглядайте логи в Render dashboard:

1. Перейдіть до вашого сервісу
2. Натисніть "Logs" tab
3. Використовуйте фільтри для пошуку помилок

## Auto Deployment

За умовчанням, Render перебудовує при push до `main`:

```bash
git push origin main  # Автоматичний деплой
```

## Manual Redeploy

1. Render Dashboard → Ваш сервіс
2. Натисніть "Manual Deploy" → "Deploy latest commit"

## Troubleshooting

### "Build failed"

```bash
# Перевірте requirements.txt
pip install -r requirements.txt

# Перевірте Python версію
python --version  # Має бути 3.10+
```

### "App crashed"

1. Перевірте логи в Render dashboard
2. Перевірте `.env` конфіг
3. Перевірте memory usage:
   ```bash
   curl https://your-app.onrender.com/api/config
   ```

### "Model not found"

Це можливо при першому старті. Чекайте 5-10 хвилин.

### "Out of memory"

Render Free tier має 0.5GB. Опції:

1. Upgrade на більший план
2. Використовуйте меншу модель
3. Оптимізуйте embedding model

## Performance Tips

### 1. Lazy Loading Models

```python
# Моделі завантажуватимуться при першому запиті
_llm_service = None

def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()  # Завантажується сюди
    return _llm_service
```

### 2. Batch Processing

```python
# Обробіть документи батчами
embeddings = embedding_service.get_embeddings_batch(chunks)
```

### 3. Кешування

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_embedding(text):
    return embedding_service.get_embedding(text)
```

## Upgrade Path

### Якщо вам потрібна більша потужність:

1. **Render Pro** (12GB RAM)
   - Підійде для Llama 2 7B
   - Швидше генерування

2. **Cloud GPU** (A100, V100)
   - Для fine-tuning
   - Для більших моделей

3. **Kubernetes Deployment**
   - Масштабування
   - Multiple instances

## Networking

### CORS

Встановлено всім дозволити:
```python
allow_origins=["*"]
```

Для production, обмежте доступ:
```python
allow_origins=["https://your-frontend.com"]
```

### Rate Limiting

Додайте slowapi:
```bash
pip install slowapi
```

```python
from slowapi import Limiter
limiter = Limiter()
limiter.limit("5/minute")(router.post("/chat"))
```

## Cost Optimization

- **Free tier**: $0 (до 750 годин/місяць)
- **Pro**: $12/месяц (більше ресурсів)
- **Paid storage**: Якщо потрібна персистенція

## Подальше

- Додайте WebSocket для streaming
- Додайте Authentication
- Налаштуйте Monitoring
-增加更多 RAG功能
