FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=38127 \
    DATA_DIR=/data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /data

EXPOSE 38127
VOLUME ["/data"]

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-38127} --workers 2 --threads 4 'app.main:create_app()'"]
