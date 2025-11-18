#!/usr/bin/env bash
set -o errexit

# instalar dependencias (Render hace pip install automáticamente si lo especificás en build)
pip install -r requirements.txt

# migraciones
python manage.py migrate --noinput

# collectstatic
python manage.py collectstatic --noinput

# createsuperuser
echo "Checking if a superuser exists"
python manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    print("Creating superuser")
    from django.core.management import call_command
    call_command('createsuperuser', '--no-input')
else:
    print("Superuser already exists. Skipping creation.")
EOF