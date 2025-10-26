FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создаем директорию для приложения
WORKDIR /app

# Копируем файлы
COPY restApi/ ./restApi/
COPY requirements.txt ./

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Expose порт
EXPOSE 8000

# Команда запуска (переопределяется в docker-compose)
CMD ["python", "restApi/main.py"]

