# Contracts_analyzer


### Для запуска проекта нужно:
- Установить обработчик пакетов uv

- Запустить бекенд, выполнив команды из корневой папки проекта:

```bash
uv sync
uv run uvicorn src.app:app --reload
```
- Запустить фронтенд, выполнив команду из корневой папки проекта:

```bash
cd frontend
npm install
npm run dev
```
- Перейти по http://localhost:5173

### Запуск через Docker

Нужен Docker (с поддержкой Docker Compose).

```bash
docker compose up -d --build
```

После сборки:
- Фронтенд: http://localhost:5173
- Бэкенд (API): http://localhost:8000 (документация — http://localhost:8000/docs)
- LLM (Ollama, модель qwen2.5:7b уже внутри образа): http://localhost:11434

Остановка: `docker compose down` (данные в томах `uploads_data`, `db_data` сохраняются).

