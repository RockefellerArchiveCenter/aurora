#!/bin/bash
#
# Script to identify new file uploads - run every 30 minutes - run log is in /data/logs/uploads
#

# Get the date and time now and from 30 minutes ago. Between 00:00 and 00:29 the date will be the previous day.

date_now="$(date +'%Y-%m-%d')"
date_now2="$(date +'%Y%m%d')"
time_now="$(date +'%T')"
date_30mins_ago="$(date -d '-30 mins' +'%Y-%m-%d')"
date_30mins_ago2="$(date -d '-30 mins' +'%Y%m%d')"
time_30mins_ago="$(date -d '-30 mins' +'%T')"
date_time_now="$date_now $time_now"
date_time_30mins_ago="$date_30mins_ago $time_30mins_ago"
echo "Run: " $date_time_now

# Build the rotated file name to check to see if it exists

rfile="/var/log/messages-"
if [ !$date_now = $date_30mins_ago ]; then
   rfile+=$date_30mins_ago2
else
   rfile+=$date_now2
fi
rfile+=".xz"

# Read in the rotated log file (if one exists) and /var/log/messages then split the single data-time
# field in the records into two separate fields.  Keep only the records contain both "sftp-server"
# and  "close" from the last 30 minutes.  Write the records to /data/new_uploads.  Add an "EOF"
# record to the file in case there are no uploads to process in this run.

if [ -e $rfile ]; then
   unxz -c -d $rfile | awk -FT '{print $1 " "  $2}' | grep "sftp\-server.*close " |
   awk -v "b=$date_time_30mins_ago" -v "e=$date_time_now" -F '.' '$1 >= b && $1 <= e' > /data/new_uploads
   awk -FT '{print $1 " "  $2}' /var/log/messages | grep "sftp\-server.*close " |
   awk -v "b=$date_time_30mins_ago" -v "e=$date_time_now" -F '.' '$1 >= b && $1 <= e' >> /data/new_uploads
   echo "***** Run:" $date_time_now "*****" >> /data/new_uploads
else
   awk -FT '{print $1 " "  $2}' /var/log/messages | grep "sftp\-server.*close " |
   awk -v "b=$date_time_30mins_ago" -v "e=$date_time_now" -F '.' '$1 >= b && $1 <= e' > /data/new_uploads
   echo "***** Run:" $date_time_now "*****" >> /data/new_uploads
fi
