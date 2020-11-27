#!/bin/bash
# get filename
# I used this script to convert Upper text in file move.info and type.info
# I do that for DLV2 (lower parameter are constant, other are unknown variable that calculate DLV-AI for us)
echo -n "Enter File Name : "
read fileName
 
# make sure file exits for reading
if [ ! -f $fileName ]; then
  echo "Filename $fileName does not exists."
  exit 1
fi
 
# convert uppercase to lowercase using tr command
tr '[A-Z]' '[a-z]' < $fileName
