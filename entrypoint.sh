#!/bin/bash

/code/wait-for-it.sh db:5432 --

# Create config.py if it doesn't exist
if [ ! -f aurora/config.py ]; then
    echo "Creating config file"
    cp aurora/config.py.example aurora/config.py
fi

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate

# Create initial organizations and users
echo "Setting up organizations and users"
python manage.py shell < ../add_orgs_for_container.py

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
