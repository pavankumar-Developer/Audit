#!/usr/bin/env bash
# Bake a settled poster frame in as frame 0 and copy each render to deliver/ with a clear name.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p deliver
declare -A NAME=( [style1-kinetic]="Style1-Kinetic" [style2-editorial]="Style2-Editorial" [style3-product]="Style3-Product" [style4-beat]="Style4-OnTheBeat" )
declare -A SIZE=( [style1-kinetic]="2160x3840" [style2-editorial]="2160x3840" [style3-product]="3840x2160" [style4-beat]="3840x2160" )
declare -A POSTER=( [style1-kinetic]="2.3" [style2-editorial]="9.6" [style3-product]="2.9" [style4-beat]="4.4" )
for f in renders/*_4k.mp4; do
  b=$(basename "$f" _4k.mp4); dir=${b%_*}; theme=${b##*_}
  label=$([ "$theme" = parkmed ] && echo "ParkmedTheme" || echo "ReferenceTheme")
  out="deliver/Parkmed-NABH_${NAME[$dir]}_${label}_${SIZE[$dir]}_60fps"
  ffmpeg -v error -y -ss "${POSTER[$dir]}" -i "$f" -frames:v 1 -q:v 2 "$out.jpg"
  ffmpeg -v error -y -i "$f" -i "$out.jpg" -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" \
    -map "[v]" -map 0:a -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -r 60 -c:a copy -movflags +faststart "$out.mp4"
  echo "$out.mp4"
done
