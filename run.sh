#!/bin/bash

echo "🚀 Запуск проекта Scribbles..."

# 1. Активация виртуального окружения
source venv/bin/activate

# 2. Установка переменных окружения (если нужно)
export $(cat .env | xargs)

# 3. Запуск основного FastAPI на 8000 (в фоне)
uvicorn app.main:app --reload --port 8000 &

# 4. Запуск админ-панели на 8001 (в фоне)
uvicorn app.admin_main:app --reload --port 8001 &

echo "🎉 Оба приложения (основное и админка) запущены!"
