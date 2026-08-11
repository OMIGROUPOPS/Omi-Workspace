#!/bin/sh
set -eu
export LC_ALL=C
output_dir=$1
input=$2
name=$(basename "$input")
gzip -cd "$input" \
  | grep -F -f /tmp/window1_v47_exam_tickers.txt \
  | gzip -1 > "$output_dir/$name"
