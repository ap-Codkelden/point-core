#!/bin/bash

d=`date +%Y-%m-%d-%H-%M-%S`
rotate=14

cd `dirname $0`

backup_dir="./$1/"

mkdir -p $backup_dir

. "./$1.sh" $d $backup_dir

find $backup_dir -type f -mtime +$rotate -exec rm '{}' \;

declare -A ftp_host=()
declare -A ftp_port=()
declare -A ftp_dir=()
declare -A ftp_user=()
declare -A ftp_pass=()

. "./.credentials"

for i in $backup_hosts; do
  lftp -e "mirror -R $backup_dir ${ftp_dir[$i]}/$1; bye;" -u "${ftp_user[$i]},${ftp_pass[$i]}" "${ftp_host[$i]}"
done
