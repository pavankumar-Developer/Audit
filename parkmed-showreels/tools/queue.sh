#!/usr/bin/env bash
# Render queue: tools/queue.sh "dir:theme:preset" ...
cd "$(dirname "$0")/.."
for job in "$@"; do
  IFS=: read -r dir theme res <<< "$job"
  start=$(date +%s)
  tools/render.sh "$dir" "$theme" "$res" && echo "$(date +%T) done $dir $theme in $(( $(date +%s)-start ))s" || echo "$(date +%T) FAILED $dir $theme"
done
