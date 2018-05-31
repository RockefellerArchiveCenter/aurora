#!/bin/bash

# Apply database migrations
/code/wait-for-it.sh db:5432 -- echo "Applying database migrations"
python manage.py migrate

# Create initial organizations
echo "Creating organizations"
python manage.py shell < ../add_orgs_for_container.py

# Create admin superuser
# echo "Creating users"
# python manage.py shell -c "from django.contrib.auth.models import User; \
#   User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')"

  # if [ ! -f aurora/config.py ]; then
  #     echo "Creating config file"
  #     cp aurora/config.py.example aurora/config.py
  # fi

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
