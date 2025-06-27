#!/usr/bin/env bash
echo "Applying migrations..."
python manage.py migrate --noinput

echo "Loading fixtures from data.json..."
python manage.py loaddata data.json

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build script finished."

exec gunicorn stage.wsgi:application --bind 0.0.0.0:$PORT