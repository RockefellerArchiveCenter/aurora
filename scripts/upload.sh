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
# field in the records into two separate fields.  There is a "T" between the date and the time.  
# Keep only the records contain both "sftp-server" and  "close" from the last 30 minutes.  
# Write the records to /data/new_uploads.  Add an "EOF" record to the file in case there 
# are no uploads to process in this run.

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

# See if there are any uploads in this run.

# Set up a counter to keep track of valid records.
# Delete the output file (/data/uploads_to_process) from the previous run.
# Check the number of lines in /data/new_uploads (2 = no new uploads, > 2 then there are uploads to process).
# Examine /data/new_uploads line-by-line.
# Parse the line into variables around spaces.
# Throw away the header and footer records ('-----' in item 0 (index origin 0).
# For upload records:
# Item 0 (index origin 0) contains the Date of the upload.
# Item 1 (index origin 0) contains the Time of the upload.
# Item 5 (index origin 0) contains the filename and path (filename may include .part on large files).
# The last item contains the size of the file (the number of this item depends on the number of spaces in the filename).
# Strip "s from around the filename.
# Remove the suffix ".part" from any file names.
# Write any records that pass the tests to /data/uploads_to_process.
# Write a "No files to process..." record to /data/uploads_to_process if there are no valid records found.
# If files were found, then update the clamav database
# uploads_to_process will be read by Python application.
# All issues with uploaded files will be processed and reported by the Python application.

a=($(wc /data/new_uploads))
lines=${a[0]}
counter=0
rm -rf /data/uploads_to_process
if [ $lines != "2" ]; then
  while IFS='' read -r line || [[ -n "$line" ]]; do
    items=( $line )
    first_word=${items[0]}
    word_count=${#items[@]}
    last_word=$(($word_count-1))
    if [ $first_word != '-----' ]; then
      filename=`echo "$line" | awk -F'"' '{print $2}'`
      file_name="$(sed 's|\.part$||i' <<<"$filename")"
      counter=$(($counter+1))
      echo "Date:"${items[0]}" Time:"${items[1]}" Size:"${items[$last_word]}" File:"$file_name >> /data/uploads_to_process
    fi
  done < "/data/new_uploads"
fi
if [ $counter = 0 ]; then
  echo "No files to process in this run." >> /data/uploads_to_process
else
  freshclam > /data/logs/clamav/clamupdate.log
fi

# End of script (upload.sh)

