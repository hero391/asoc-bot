FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHECKIN_HOST=0.0.0.0 \
    CHECKIN_COOKIE_SECURE=true \
    DB_PATH=/data/aso.db

WORKDIR /app

COPY venv/Scripts/requirements.txt /app/venv/Scripts/requirements.txt
RUN pip install --no-cache-dir -r /app/venv/Scripts/requirements.txt

COPY venv/Scripts/*.py /app/venv/Scripts/
COPY venv/data/sessions.csv /app/venv/data/sessions.csv

CMD ["python", "/app/venv/Scripts/railway_app.py"]
