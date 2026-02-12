# Backend (FastAPI + OpenAI)

## Что делает
- `POST /api/suggest` принимает `{ "text": "..." }`
- Генерирует 9 вариантов:
  - `branch`
  - `commit`
- Ограничение по IP: `3 запроса / 10 минут`

## Запуск
1. Создать и активировать виртуальное окружение:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Настроить переменные:
```bash
cp .env.example .env
```

4. Запустить сервер:
```bash
export $(grep -v '^#' .env | xargs) && uvicorn main:app --reload --port 8000
```

## Пример запроса
```bash
curl -X POST "http://localhost:8000/api/suggest" \
  -H "Content-Type: application/json" \
  -d '{"text":"Добавил валидацию формы входа и обработку ошибок API"}'
```
