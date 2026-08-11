#!/bin/sh
set -eu
output=/tmp/window1_v47_exam_filtered_members
member_list=${1:-/tmp/window1_v47_exam_frozen_raw_files.txt}
mkdir -p "$output"
xargs -a "$member_list" -n 1 -P 4 /tmp/window1_v47_exam_filter_one.sh "$output"
