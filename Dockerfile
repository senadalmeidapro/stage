# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Si tu utilises psycopg2
RUN apt-get update \
  && apt-get install -y gcc libpq-dev netcat \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/build.sh
# Automatisation du collectstatic
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "stage.wsgi:application", "--bind", "0.0.0.0:$PORT"]
