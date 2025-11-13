#!/usr/bin/env bash
set -o errexit

# instalar dependencias (Render hace pip install automáticamente si lo especificás en build)
pip install -r requirements.txt

# migraciones
python manage.py migrate --noinput

# collectstatic
python manage.py collectstatic --noinput

# createsuperuser
python manage.py createsuperuser --no-input