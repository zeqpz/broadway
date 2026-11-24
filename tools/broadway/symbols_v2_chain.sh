#!/bin/sh
# Symbols v2 install chain (2026-11-22): the redrawn <ID>_v2.png become the pipeline's <ID>_v1.png (the first set kept in
# art/broadway-src/sym_v1_old/), then 4K -> icons -> Blender (every clip) -> QA -> pack -> record tiers -> phone sheets.
set -e
cd "$(dirname "$0")/../.."
PY=/c/Users/CooperHinkel/Documents/ClaudeRoblox/smukiez-slot/.venv/Scripts/python.exe
S=art/broadway-src
mkdir -p $S/sym_v1_old
for id in H1 H2 H3 H4 H5 H6 H7 L1 L3 L4 M BS ES; do
  [ -f $S/sym_v1_old/${id}_v1.png ] || cp $S/${id}_v1.png $S/sym_v1_old/
  cp $S/${id}_v2.png $S/${id}_v1.png
done
echo "== upscale"; $PY tools/broadway/upscale4k.py sym
echo "== icons"; $PY tools/broadway/prep_icons.py
echo "== blender"; sh tools/broadway/blender/render_all.sh
echo "== qa"; $PY tools/broadway/qa_sym.py all > art/blender/qa/_report_all.txt 2>&1 || true
echo "== pack"; $PY tools/blender/pack_frames.py all
echo "== tiers"; rm -rf art/blender/renders/M_gold; $PY tools/broadway/record_tiers.py
echo "== phone sheets"; $PY tools/broadway/make_phone_sheets.py
echo "== phone copies"; $PY tools/broadway/make_mobile_art.py > /dev/null
echo "CHAIN DONE"
