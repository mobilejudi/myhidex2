FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY pyproject.toml /app/
RUN pip install --upgrade pip && pip install -e .

COPY . /app

EXPOSE 8000
CMD ["python","app_real.py"]
