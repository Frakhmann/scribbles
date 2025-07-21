<<<<<<< HEAD

#!/bin/bash
echo "🚀 Запуск Scribbles (Render production)..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
=======
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

# 5. (Опционально) можно открыть Swagger в браузере:
xdg-open http://127.0.0.1:8000/docs > /dev/null 2>&1

echo "🎉 Оба приложения (основное и админка) запущены!"
>>>>>>> 61f3ab9 (admin panel)
