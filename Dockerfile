# Используем официальный Python образ
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду запуска (Procfile Koyeb тоже использует)
CMD ["python", "main.py"]
