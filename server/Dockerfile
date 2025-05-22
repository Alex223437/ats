# Используем официальный образ Python
FROM python:3.11

# Устанавливаем системные зависимости (для tensorflow, matplotlib, и пр.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app
COPY requirements.txt /app/requirements.txt
# dev only
COPY .env /app/.env 

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt  

# Открываем порт для FastAPI
EXPOSE 8000

# Запускаем Alembic миграции и потом FastAPI
# CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT"]

# dev 
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]