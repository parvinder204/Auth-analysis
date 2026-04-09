#!/bin/bash
set -e

echo "Setting up Django Auth Showcase..."

cd "$(dirname "$0")"

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt --quiet

python manage.py migrate --run-syncdb

python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
"

echo ""
echo "Django setup complete."
echo "Run: source .venv/bin/activate && python manage.py runserver 8000"