#!/bin/bash

/code/wait-for-it.sh db:5432 --

# Start clamav services
echo "Starting ClamAV"
clamd

# Start SSH
if [[ -z "${TRAVIS_CI}" ]]; then
  echo "starting SSH"
  /usr/sbin/sshd -f /etc/ssh2/sshd_config
fi

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
python manage.py shell < ./setup_objects.py

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:${APPLICATION_PORT}
