FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHECKIN_HOST=0.0.0.0 \
    CHECKIN_COOKIE_SECURE=true \
    DB_PATH=/data/aso.db

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/ /app/app/
COPY data/sessions.csv /app/data/sessions.csv

CMD ["python", "/app/app/railway_app.py"]
