FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Lance Gunicorn sur le port 8000 pour servir Django
CMD ["gunicorn", "stage.wsgi:application", "--bind", "0.0.0.0:8000"]
