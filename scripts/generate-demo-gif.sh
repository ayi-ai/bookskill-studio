#!/usr/bin/env bash
set -euo pipefail

# Optional: regenerate an animated demo GIF when `vhs` is installed.
# brew install vhs

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAPE="$ROOT/scripts/demo.tape"
OUT="$ROOT/assets/demo.gif"

if ! command -v vhs >/dev/null 2>&1; then
  echo "vhs not found. Install with: brew install vhs" >&2
  exit 1
fi

cd "$ROOT"
vhs "$TAPE"
mv demo.gif "$OUT"
echo "Wrote $OUT"
