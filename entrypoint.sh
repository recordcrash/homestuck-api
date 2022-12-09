#!/bin/sh
# Install requirements
echo "Installing requirements"
python -m pip install -r requirements.txt

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Load data from fixtures folder
# echo "Load data from fixtures folder"
# python manage.py loaddata fixtures/*

# Create default superuser
python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL

# Clone hsmusic repos if they don't exist, update if they do
# These are only needed for the "manage.py import_hsmusic_yaml" command
git -C hsmusic-data pull || git clone https://github.com/hsmusic/hsmusic-data.git hsmusic-data
git -C hsmusic-media pull || git clone https://nebula.ed1.club/git/hsmusic-media/ hsmusic-media

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000

exec "$@"