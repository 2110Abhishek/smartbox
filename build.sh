#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static assets..."
python manage.py collectstatic --noinput

echo "Seeding demo inventory & boxes..."
python manage.py seed_demo_data

echo "Build completed successfully!"

