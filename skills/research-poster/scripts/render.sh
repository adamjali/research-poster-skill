#!/bin/bash
# render.sh <pptx> <out_pdf> <out_png> [scale]
# Render a .pptx to PDF then rasterize to PNG, cross-platform.
# Prefers LibreOffice headless (Linux / Windows / macOS). On macOS with no working
# LibreOffice, falls back to Microsoft PowerPoint via AppleScript. PNG via pypdfium2
# (self-contained, no poppler needed).
set -u
SRC="$1"; PDF="$2"; PNG="$3"; SCALE="${4:-1.7}"
rm -f "$PDF"
OUTDIR="$(cd "$(dirname "$PDF")" && pwd)"
BASE="$(basename "${SRC%.*}")"

find_libreoffice() {
  for c in soffice libreoffice; do
    if command -v "$c" >/dev/null 2>&1 && "$c" --version >/dev/null 2>&1; then echo "$c"; return 0; fi
  done
  return 1
}

render_libreoffice() {
  "$1" --headless --convert-to pdf --outdir "$OUTDIR" "$SRC" >/dev/null 2>&1
  if [ -f "$OUTDIR/$BASE.pdf" ] && [ "$OUTDIR/$BASE.pdf" != "$PDF" ]; then mv "$OUTDIR/$BASE.pdf" "$PDF"; fi
  [ -f "$PDF" ]
}

render_powerpoint_macos() {
  [ "$(uname)" = "Darwin" ] || return 1
  command -v osascript >/dev/null 2>&1 || return 1
  osascript -e 'tell application "Microsoft PowerPoint" to quit saving no' 2>/dev/null; sleep 1
  pkill -x "Microsoft PowerPoint" 2>/dev/null; sleep 1
  local try=0
  while [ $try -lt 2 ]; do
    osascript >/dev/null 2>&1 <<OSA
with timeout of 280 seconds
	tell application "Microsoft PowerPoint" to launch
	delay 3
	tell application "Microsoft PowerPoint"
		open POSIX file "$SRC"
		delay 1
		set d to active presentation
		save d in (POSIX file "$PDF" as string) as save as PDF
		close d saving no
	end tell
end timeout
OSA
    [ -f "$PDF" ] && break
    pkill -x "Microsoft PowerPoint" 2>/dev/null; sleep 3; try=$((try+1))
  done
  osascript -e 'tell application "Microsoft PowerPoint" to quit saving no' 2>/dev/null
  [ -f "$PDF" ]
}

if LO="$(find_libreoffice)"; then render_libreoffice "$LO" || true; fi
[ -f "$PDF" ] || render_powerpoint_macos || true
if [ ! -f "$PDF" ]; then
  echo "RENDER FAILED: install LibreOffice (soffice/libreoffice on PATH) or run on macOS with Microsoft PowerPoint." >&2
  exit 1
fi
python3 -c "import pypdfium2 as p; im=p.PdfDocument('$PDF')[0].render(scale=$SCALE).to_pil(); im.save('$PNG'); print('rendered', im.size)"
