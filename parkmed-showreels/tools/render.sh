#!/usr/bin/env bash
# tools/render.sh <style-dir> <theme> <resolution-preset>
set -euo pipefail
cd "$(dirname "$0")/.."
dir="$1"; theme="$2"; res="$3"
out="renders/${dir}_${theme}_4k.mp4"
( cd "$dir" && npx hyperframes render --quality delivery --fps 60 --resolution "$res" --variables "{\"theme\":\"$theme\"}" --output "../$out" ) > "renders/${dir}_${theme}.log" 2>&1
echo "rendered $out"
