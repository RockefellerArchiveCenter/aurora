#!/bin/bash
#
# Script to check that clamd is running on port 3310.  If not, restart clamd service
#
#log_file="/data/logs/clamd/clamd.log"
date_this_run=$(date)
var=$(lsof -t -itcp:3310)
if [ $? = 1 ]; then
# Need to restart clamd service as it is not running
  systemctl restart clamd
  echo $date_this_run' - Clamd was NOT running - service restarted'
else
  echo $date_this_run' - Clamd was running - no action taken'
fi
