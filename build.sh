#!/usr/bin/env bash

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Loading fixtures from data.json..."
python manage.py loaddata data.json

echo "Checking/Creating superuser..."
# Vérifie si l'utilisateur existe déjà
if echo "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='cheche').exists())" | python manage.py shell | grep -q "True"; then
    echo "Superuser 'cheche' already exists. Skipping creation."
else
    echo "Creating superuser..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('cheche', '', 'alibababj')" | python manage.py shell
    echo "Superuser created:"
    echo "Username: cheche"
    echo "Password: alibababj"
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build script finished."

exec gunicorn stage.wsgi:application --bind 0.0.0.0:$PORT
