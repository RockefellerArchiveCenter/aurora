#!/bin/bash

# Apply database migrations
/code/wait-for-it.sh db:5432 -- echo "Applying database migrations"
python manage.py migrate

  # if [ ! -f aurora/config.py ]; then
  #     echo "Creating config file"
  #     cp aurora/config.py.example aurora/config.py
  # fi

# Create initial organizations and users
echo "Creating organizations"
python manage.py shell < ../add_orgs_for_container.py

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
