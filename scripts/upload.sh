#!/bin/bash
#
# Script to identify new file uploads - run every 5 minutes.
#
# This script requires bash version 4+. 
#
# This script needs write access to certain
# directory paths as noted below.
#
# Set the following variables for your environment.
output_file="/data/uploads_to_process"
dirsearch_file="/data/dirseach_temp"
dirlist_file="/data/dirlist_temp"
# Purge the temp files from the previous run
rm -rf $dirlist_search
rm -rf $dirlist_file
# End of variable list
date_this_run=$(date)
echo "Start run: "$(date)
find /data/org*/upload/ -type f -print0 > $dirsearch_file
mapfile dirtst -t < $dirsearch_file
testdirs=${#dirtst[@]}
if [ $testdirs -eq 0 ]; then
  echo $date_this_run": No files to process in this run." >> $output_file
  echo "End run:   "$(date)
else  
  rm -rf $dirsearch_file
# Find any non-empty directories.
  find /data/org*/upload/ -type f -print0 | xargs -0 -n 1 dirname | sort -u > $dirsearch_file
  mapfile dirs -t < $dirsearch_file
  numdirs=${#dirs[@]}
# Process the directories.
  if [ $numdirs -gt 0 ]; then
    dir=${dirs[0]}
    dir2="$(echo "$dir"|tr -d '\n')"
    find "$dir2" -type f > $dirlist_file
    mapfile dirfiles -t < $dirlist_file
    numfiles=${#dirfiles[@]}
    x=0
    filemax=$((numfiles-1))
# Process the files.
    while [ $x -le $filemax ]; do
      filepath=${dirfiles[$x]}
      filepath2="$(echo "$filepath"|tr -d '\n')"
      filename=$(basename "$filepath2")
# Ignore files with ".filepart" in the name.
      if [[ $filename != *".filepart"* ]]; then
        path=$(dirname "$filepath2")
        first_string=$filepath2
        second_string=processing
        nlocation=${first_string/upload/$second_string}
        nlocation1="$(echo "$nlocation"|tr -d '\n')"
        first_string=$path
        second_string=processing
        nlocation2=${first_string/upload/$second_string} 
# Check to see if the target (../processing/..) directory path for each file exists.
# If it does then move the file - warn only if file already exists.
# If not it is necessary to build the path prior to moving the file.      
        if [ -d "$nlocation2" ]; then
          if [ -f "$nlocation1" ]; then
            echo $date_this_run": File: "$nlocation1" already exists and will be replaced." >> $output_file
          fi
          mv -f "$filepath2" "nlocation1"
          echo $date_this_run": New file: "$nlocation1 >> $output_file
        else
          mkdir -p "$nlocation2"
          echo $date_this_run": New directory created: "$nlocation2 >> $output_file
          mv -f "$filepath2" "$nlocation1"      
          echo $date_this_run": New file: "$nlocation1 >> $output_file
        fi
      fi
      x=$((x+1))
    done   
  else
    echo $date_this_run": No files to process in this run." >> $output_file
  fi
  echo "End run:   "$(date)
fi
#
# End of script 
#
