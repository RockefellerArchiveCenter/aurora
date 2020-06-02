#!/bin/bash

# Script to import set of sample bags
# Copies files to data upload directory and then runs cron

cp -r ../sample_bags/* /data/donororganization/upload/
chown -R donor /data/donororganization/upload/
python manage.py runcrons bag_transfer.lib.cron.DiscoverTransfers
