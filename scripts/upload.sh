#!/bin/bash
#
# Script to identify new file uploads - run every 30 minutes
#
#
# Set the following variables for your environment - you may also need to adjust the name and format 
# of the rotated messages file if the format differs from the default used below.
#
path_to_messages_log="/var/log/"
messages_file_name="messages"
path_to_rotated_messages_log="/var/log/"
path_to_temp_extract_file="/data/"
temp_extract_file_name="new_uploads"
path_to_clamav_log_file="/data/logs/clamav/"
clamav_update_log_file_name="/clamupdate.log"
path_to_output_file="/data/"
output_file_name="uploads_to_process"
#
# End of Variable setup
#
# Build filenames and paths
#
messages_file=$path_to_messages_log
messages_file+=$messages_file_name
clamav_log=$path_to_clamav_log_file
clamav_log+=$clam_update_log_file_name
temp_file=$path_to_temp_extract_file
temp_file+=$temp_extract_file_name
output_file=$path_to_output_file
output_file+=$output_file_name
#
# Build the rotated file name to check to see if it exists (local format is /var/log/messages-YYMMDD.xz - adjust as needed).
#
rfile=$path_to_rotated_messages_log
rfile+="messages-"
if [ !$date_now = $date_30mins_ago ]; then
   rfile+=$date_30mins_ago2
else
   rfile+=$date_now2
fi
rfile+=".xz"
#
# Get the date and time now and from 30 minutes ago. 
#
date_now="$(date +'%Y-%m-%d')"
date_now2="$(date +'%Y%m%d')"
time_now="$(date +'%T')"
date_30mins_ago="$(date -d '-30 mins' +'%Y-%m-%d')"
date_30mins_ago2="$(date -d '-30 mins' +'%Y%m%d')"
time_30mins_ago="$(date -d '-30 mins' +'%T')"
date_time_now="$date_now $time_now"
date_time_30mins_ago="$date_30mins_ago $time_30mins_ago"
echo "Run: " $date_time_now
#
# Read in the rotated log file if one exists ($rfile) and $messages_file then split the single data-time
# field in the records into two separate fields.  There is a "T" between the date and the time.  
# Keep only the records contain both "sftp-server" and  "close" from the last 30 minutes.  
# Write the records to $temp_file.  Add an "EOF" record to the file in case there 
# are no uploads to process in this run.
#
echo "----- START ***** Run:" $date_time_now "-----" > $temp_file
if [ -e $rfile ]; then
   unxz -c -d $rfile | awk -FT '{print $1 " "  $2}' | grep "sftp\-server.*close " |
   awk -v "b=$date_time_30mins_ago" -v "e=$date_time_now" -F '.' '$1 >= b && $1 <= e' >> $temp_file
   awk -FT '{print $1 " "  $2}' $messages_file | grep "sftp\-server.*close " |
   awk -v "b=$date_time_30mins_ago" -v "e=$date_time_now" -F '.' '$1 >= b && $1 <= e' >> $temp_file
   echo "----- END ***** Run:" $date_time_now "-----" >> $temp_file
else
   awk -FT '{print $1 " "  $2}' $messages_file | grep "sftp\-server.*close " |
   awk -v "b=$date_time_30mins_ago" -v "e=$date_time_now" -F '.' '$1 >= b && $1 <= e' >> $temp_file
   echo "----- END ***** Run:" $date_time_now "-----" >> $temp_file
fi
#
# See if there are any uploads in this run.
#
# Set up a counter to keep track of valid records.
# Delete the output file ($output_file) from the previous run.
# Check the number of lines in $temp_file (2 = no new uploads, > 2 then there are uploads to process).
# Examine $temp_file line-by-line.
# Parse the line into variables around spaces.
# Throw away the header and footer records ('-----' in item 0 (index origin 0).
# For upload records:
# Item 0 (index origin 0) contains the Date of the upload.
# Item 1 (index origin 0) contains the Time of the upload.
# Item 5 (index origin 0) contains the filename and path (filename may include .part on large files).
# The last item contains the size of the file (the number of this item depends on the number of spaces in the filename).
# Strip "s from around the filename.
# Remove the suffix ".part" from any file names.
# Write any records that pass the tests to $output_file.
# Write a "No files to process..." record to $output_file if there are no valid records found.
# If files were found, then update the clamav database
# $output_file will be read by Python application.
# All issues with uploaded files will be processed and reported by the Python application.
#
a=($(wc $temp_file))
lines=${a[0]}
counter=0
rm -rf $output_file
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
      echo "Date:"${items[0]}" Time:"${items[1]}" Size:"${items[$last_word]}" File:"$file_name >> $output_file
    fi
  done < "$temp_file"
fi
if [ $counter = 0 ]; then
  echo "No files to process in this run." >> $output_file
else
  freshclam > $clamav_log
fi
#
# End of script (upload.sh)
#
