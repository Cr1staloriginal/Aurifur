# Используем Python 3.13
FROM python:3.13-slim

# Рабочая директория
WORKDIR /app

# Копируем все файлы проекта
COPY . /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Запуск бота
CMD ["python", "main.py"]
