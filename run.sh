
#!/bin/bash
echo "🚀 Запуск Scribbles (Render production)..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT

#!/bin/bash

