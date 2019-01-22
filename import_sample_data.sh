#!/bin/bash

# Script to import set of sample bags
# Copies files to data upload directory and then runs cron

cp -r ../sample_bags/* /data/org2/upload/
chown -R donor /data/org2/upload/
python manage.py runcrons bag_transfer.lib.cron.DiscoverTransfers
