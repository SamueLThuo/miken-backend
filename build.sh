#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if env vars are set
if [[ $DJANGO_SUPERUSER_USERNAME && $DJANGO_SUPERUSER_EMAIL && $DJANGO_SUPERUSER_PASSWORD ]]; then
  echo "Creating superuser..."
  python manage.py createsuperuser \
    --no-input \
    --username $DJANGO_SUPERUSER_USERNAME \
    --email $DJANGO_SUPERUSER_EMAIL || true
fi
