#!/bin/sh
set -eu
export LC_ALL=C
member_list=${1:-/tmp/window1_v47_exam_frozen_raw_files.txt}
output_dir=${2:-/tmp/window1_v47_exam_filtered_members}
failure_list=${3:-/tmp/window1_v47_exam_failed_members.txt}
: > "$failure_list"
while IFS= read -r source
do
  output="$output_dir/$(basename "$source")"
  if [ ! -f "$output" ] || ! gzip -t "$output" 2>/dev/null
  then
    echo "$source" >> "$failure_list"
  fi
done < "$member_list"
printf 'FAILED=%s\n' "$(wc -l < "$failure_list")"
sha256sum "$failure_list"
