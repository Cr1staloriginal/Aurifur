FROM python:3.13-slim

WORKDIR /app

# Копируем всё из проекта
COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
