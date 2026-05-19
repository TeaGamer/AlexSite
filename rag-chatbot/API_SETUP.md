# RAG Chatbot - API Configuration Guide

Система була перенесена з **локального LLM (Llama 2)** на використання **зовнішніх LLM API**. Система RAG (вектор БД, embeddings) залишилась як є.

## 🔄 Що змінилось

| Компонент | Було | Стало |
|-----------|------|-------|
| **LLM** | Llama 2 (локально) | OpenAI/Anthropic/Cohere API |
| **Embeddings** | DistilBERT (локально) | DistilBERT (локально) ✅ |
| **Vector Store** | Chroma | Chroma ✅ |
| **RAG System** | Чітка система | Чітка система ✅ |

## ⚙️ Налаштування

### 1. Установка залежностей

```bash
pip install -r requirements.txt
```

### 2. Отримання API ключа

Виберіть одного провайдера:

#### **OpenAI (Рекомендується)**
1. Перейдіть на https://platform.openai.com/api-keys
2. Створіть новий API ключ
3. Скопіюйте ключ (почнеться з `sk-`)

#### **Anthropic (Claude)**
1. Перейдіть на https://console.anthropic.com/
2. Створіть API ключ
3. Скопіюйте ключ

#### **Cohere**
1. Перейдіть на https://dashboard.cohere.com/
2. Створіть API ключ
3. Скопіюйте ключ

### 3. Конфігурування .env файлу

Скопіюйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Відредагуйте `.env` з вашими параметрами:

```bash
# For OpenAI
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-actual-key-here
LLM_MODEL_NAME=gpt-3.5-turbo  # або gpt-4

# For Anthropic
# LLM_PROVIDER=anthropic
# LLM_API_KEY=sk-ant-your-actual-key-here
# LLM_MODEL_NAME=claude-3-sonnet-20240229

# For Cohere
# LLM_PROVIDER=cohere
# LLM_API_KEY=your-cohere-key
# LLM_MODEL_NAME=command

# Embeddings (залишиться локально)
EMBEDDING_MODEL_NAME=sentence-transformers/distilbert-base-uncased
DEVICE=cpu  # або cuda для GPU

# Інші параметри
MAX_TOKENS=512
TEMPERATURE=0.7
TOP_P=0.9
```

## 🚀 Запуск

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Свагер буде доступний на: http://localhost:8000/docs

## 📝 Поддерживаємі моделі

### OpenAI
- `gpt-3.5-turbo` (швидка, дешева)
- `gpt-4` (потужна, дорога)
- `gpt-4-turbo` (баланс)

### Anthropic
- `claude-3-sonnet-20240229` (швидка)
- `claude-3-opus-20240229` (потужна)
- `claude-3-haiku-20240307` (найшвидша)

### Cohere
- `command` (стандартна)
- `command-light` (легша)

## 💡 Приклад використання

### 1. Завантажити документ
```bash
curl -X POST "http://localhost:8000/api/rag/upload-document" \
  -F "file=@study_program.pdf"
```

### 2. Задати питання
```bash
curl -X POST "http://localhost:8000/api/rag/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Які курси входять до першого семестру?",
    "session_id": "user123",
    "top_k": 3
  }'
```

## 🔐 Безпека

- **НІКОЛИ** не комітьте `.env` з API ключами в Git
- Файл `.gitignore` вже налаштований
- Переглядайте права доступу до API ключів

## 📊 Вартість

### OpenAI (приблизно)
- GPT-3.5: $0.0005 за 1K токенів (вхід), $0.0015 за 1K (вихід)
- GPT-4: $0.03 за 1K (вхід), $0.06 за 1K (вихід)

### Anthropic
- Claude 3 Sonnet: $3 за 1M (вхід), $15 за 1M (вихід)

### Cohere
- Command: $1 за 1M токенів (вхід), $3 за 1M (вихід)

## 🐛 Виправлення помилок

### Помилка: "No API key provided"
- Переконайтесь, що `.env`ファイл існує
- Перевірте, що `LLM_API_KEY` встановлено

### Помилка: "openai package not installed"
```bash
pip install openai
```

### Помилка: "Model not found"
- Переконайтесь, що назва моделі правильна
- Перевірте, що у вас є доступ до цієї моделі

## ✨ Переваги

✅ **Без завантаження моделей** - економія диску  
✅ **Краща якість** - використання найновіших моделей  
✅ **Гнучкість** - легко змінювати провайдер  
✅ **Масштабованість** - API справляється з навантаженням  
✅ **RAG залишається локальним** - приватні embeddings  

## 📚 Додаткові ресурси

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic Docs](https://docs.anthropic.com/)
- [Cohere API Docs](https://docs.cohere.com/)
