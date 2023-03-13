FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && apt-get install -y default-libmysqlclient-dev gcc curl git docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY . .

EXPOSE 8000

CMD ./run_backend.sh
