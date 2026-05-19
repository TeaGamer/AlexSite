# ⚡ Швидкий старт з OpenAI API

Слідуйте цим кроками, щоб швидко почати роботу.

## 🔑 Крок 1: Отримайте OpenAI API ключ (2 хвилини)

1. Перейдіть на https://platform.openai.com/api-keys
2. Натисніть **"Create new secret key"**
3. Скопіюйте ключ (приклад: `sk-proj-xxxxxxxxxxxxx`)

## 📥 Крок 2: Налаштуйте проект (5 хвилин)

```bash
# Перейти до проекту
cd rag-chatbot

# Установити залежності
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
```

## ✏️ Крок 3: Вставте API ключ

Відредагуйте файл `.env`:

```bash
# Відкрийте .env у текстовому редакторі і замініть:
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-ВАШ-КЛЮЧ-ТУТTTT  # 👈 Вставте сюди ключ
LLM_MODEL_NAME=gpt-3.5-turbo
```

## 🚀 Крок 4: Запустіть сервер

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ви повинні побачити:
```
INFO:     Application startup complete
```

Відкрийте браузер: http://localhost:8000/docs

## 🧪 Крок 5: Тестування

### 1️⃣ Завантажте PDF

1. У Swagger UI знайдіть **`/api/rag/upload-document`**
2. Натисніть **"Try it out"**
3. Виберіть PDF файл
4. Натисніть **"Execute"**

### 2️⃣ Задайте питання

1. Знайдіть **`/api/rag/chat`**
2. Натисніть **"Try it out"**
3. Введіть JSON:

```json
{
  "question": "Про що цей документ?",
  "session_id": "test_user",
  "top_k": 3
}
```

4. Натисніть **"Execute"**

## 💰 Вартість

- **Перші запити - бесплатно!** OpenAI дає $5 кредиту для тестування
- Після цього: ~$0.001 за 1000 токенів

## 🔄 Альтернативні провайдери

Якщо хочете спробувати інших:

### Anthropic (Claude)
```bash
pip install anthropic
```
Потім в `.env`:
```
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-xxxxxxxxxxxxx
LLM_MODEL_NAME=claude-3-sonnet-20240229
```

### Cohere
```bash
pip install cohere
```
Потім в `.env`:
```
LLM_PROVIDER=cohere
LLM_API_KEY=xxxxxxxxxxxxx
LLM_MODEL_NAME=command
```

## ❓ Проблеми?

| Помилка | Рішення |
|---------|---------|
| "No API key provided" | Перевірте `.env` файл |
| "401 Unauthorized" | Ключ неправильний або закінчився кредит |
| "Rate limit exceeded" | Чекайте кілька секунд |
| "Module not found" | Запустіть `pip install -r requirements.txt` |

## 📚 Наступні кроки

- Прочитайте [API_SETUP.md](API_SETUP.md) для деталей
- Завантажуйте свої документи
- Налаштуйте промпти в [llm_service.py](app/services/llm_service.py)
- Розгорніть на [Render](DEPLOY_RENDER.md)

Успіхів! 🎉
