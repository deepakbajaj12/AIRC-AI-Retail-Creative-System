#!/usr/bin/env sh
set -eu

# Downloads Inter Regular TTF into this folder.
# Source: official Inter site (rsms.me).

OUT_FILE="$(cd "$(dirname "$0")" && pwd)/Inter-Regular.ttf"
URL="https://rsms.me/inter/font-files/Inter-Regular.ttf"

echo "Downloading Inter-Regular.ttf..."
if command -v curl >/dev/null 2>&1; then
  curl -L "$URL" -o "$OUT_FILE"
elif command -v wget >/dev/null 2>&1; then
  wget "$URL" -O "$OUT_FILE"
else
  echo "Need curl or wget" >&2
  exit 1
fi

echo "Saved: $OUT_FILE"
