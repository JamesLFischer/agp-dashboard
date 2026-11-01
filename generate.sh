#!/usr/bin/env bash
set -euo pipefail
ROOT=/workspace/agp
DASH=$ROOT/dashboard
mkdir -p "$DASH/assets" "$DASH/evidence"
cp -f "$ROOT/v4/METRICS.json" "$DASH/assets/METRICS.json" 2>/dev/null || true
cp -f "$ROOT/v4/METRICS_HISTORY.jsonl" "$DASH/assets/METRICS_HISTORY.jsonl" 2>/dev/null || true
cp -f "$ROOT/v4/dashboard.png" "$DASH/assets/dashboard.png" 2>/dev/null || true
EV_SRCS=(
  "$ROOT/v4/dashboard.png" "$ROOT/v4/cmp.jpg" "$ROOT/v4/emu.jpg" "$ROOT/v4/emu2.jpg"
  "$ROOT/v4/ci.png" "$ROOT/v4/c3s.png" "$ROOT/v4/cal_home.png" "$ROOT/v4/cal_deck_equipped.png"
  "$ROOT/v4/cal_coll_s0.png" "$ROOT/v4/cal_cr_a.png" "$ROOT/contact.png" "$ROOT/sheet.png"
  "$ROOT/home.png" "$ROOT/sheet_nav.png" "$ROOT/drive/sheet.png" "$ROOT/drive/sr_0826_1844.mp4"
)
rm -rf "$DASH/evidence"
mkdir -p "$DASH/evidence"
i=0
MANIFEST="[]"
for f in "${EV_SRCS[@]}"; do
  if [ -f "$f" ]; then
    bn=$(basename "$f")
    dest="$DASH/evidence/${i}_${bn}"
    cp -f "$f" "$dest"
    ext_l=$(echo "${bn##*.}" | tr '[:upper:]' '[:lower:]')
    kind=image
    [[ "$ext_l" == "mp4" || "$ext_l" == "webm" || "$ext_l" == "mov" ]] && kind=video
    MANIFEST=$(python3 -c "import json,sys; m=json.loads(sys.argv[1]); m.append({'src':'evidence/'+sys.argv[2],'kind':sys.argv[3],'name':sys.argv[4]}); print(json.dumps(m))" "$MANIFEST" "$(basename "$dest")" "$kind" "$bn")
    i=$((i+1))
  fi
done
printf '%s\n' "$MANIFEST" > "$DASH/assets/evidence.json"
python3 "$DASH/build_site.py"
