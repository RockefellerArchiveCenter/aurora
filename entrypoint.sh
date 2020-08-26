#!/bin/bash

/code/wait-for-it.sh db:5432 --

# Start SSH
/usr/sbin/sshd

# Start clamav services
/etc/init.d/clamav-daemon start
/etc/init.d/clamav-freshclam start

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
python manage.py shell < ../setup_objects.py

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
