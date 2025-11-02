# Используем официальный Python 3.13
FROM python:3.13-slim

# Создаём рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы проекта внутрь контейнера
COPY . /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Команда запуска бота
CMD ["python", "main.py"]
