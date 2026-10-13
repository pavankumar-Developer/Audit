#!/usr/bin/env bash
# Copy shared assets + synthesized score into a style's composition folder.
#   tools/assemble.sh s4 style4-beat
set -euo pipefail
cd "$(dirname "$0")/.."
s="$1"; dir="$2"
mkdir -p "$dir/assets/audio"
rm -rf "$dir/assets/fonts" "$dir/assets/logo" "$dir/assets/vendor"
cp -r shared/fonts shared/logo shared/vendor "$dir/assets/"
cp shared/kit.js shared/fonts.css "$dir/assets/"
python3 tools/score.py "$s" "$dir/assets/audio/score.wav" "$dir/assets/audio/score.json"
python3 - "$dir" <<'EOF'
import json, sys
d = sys.argv[1]
j = json.load(open(f"{d}/assets/audio/score.json"))
open(f"{d}/assets/beats.js", "w").write("window.BEATS = " + json.dumps({k: j[k] for k in ("bpm", "beat", "beats", "cuts", "cutBeats", "env60")}) + ";\n")
EOF
echo "assembled $dir"
