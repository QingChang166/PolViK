#!/usr/bin/env bash
# Restore the geodata evicted from this repository.
#
# Evicted 2026-09-17 to keep the working tree small: 18,054 files / 1.85 GB of
# raw SUNGEO historical boundaries, derived PRIO-GRID assignment outputs, a
# pickled model and rendered figures. The processed YAML — the actual knowledge
# graph — is tracked in git and needs nothing from here.
#
# Everything restored by this script also remains in this repository's git
# history; see docs/EVICTED_FILES.md for how to recover individual files without
# a download.
#
# Usage:
#   scripts/fetch_raw_data.sh              restore into the repository root
#   scripts/fetch_raw_data.sh /some/dir    restore elsewhere
#   scripts/fetch_raw_data.sh --verify     re-check an existing restore, download nothing
set -euo pipefail

DROPBOX_URL="https://www.dropbox.com/scl/fo/5ij6n7fhptar0bnxjowsi/AFRI8RCfMNaiGpg5wicH3AY?rlkey=jjxdd8wpb1amlmoxa840fxjsj&dl=1"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$HERE/raw_data_manifest.txt"
VERIFY_ONLY=0
[ "${1:-}" = "--verify" ] && { VERIFY_ONLY=1; shift; }
DEST="${1:-$(cd "$HERE/.." && pwd)}"

[ -f "$MANIFEST" ] || { echo "error: manifest not found at $MANIFEST" >&2; exit 1; }
EXPECTED=$(wc -l < "$MANIFEST" | tr -d ' ')

verify() {
  echo "Verifying $EXPECTED files against the manifest ..."
  if ( cd "$DEST" && shasum -a 256 -c "$MANIFEST" --quiet ); then
    echo "OK: all $EXPECTED files match."
    return 0
  fi
  echo "error: verification failed — the restore is incomplete or corrupt." >&2
  echo "       Re-run without --verify to download again." >&2
  return 1
}

if [ "$VERIFY_ONLY" -eq 1 ]; then
  verify; exit $?
fi

command -v curl  >/dev/null || { echo "error: curl not found"   >&2; exit 1; }
command -v unzip >/dev/null || { echo "error: unzip not found"  >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Downloading polvik-raw-geodata.zip (about 1.9 GB uncompressed) ..."
curl -L --fail --progress-bar "$DROPBOX_URL" -o "$TMP/raw-geodata.zip"

# A Dropbox link that has expired or needs a login returns an HTML page with a
# 200 status, which unzip would reject with a confusing error. Catch it here.
if ! unzip -tqq "$TMP/raw-geodata.zip" >/dev/null 2>&1; then
  echo "error: the download is not a valid zip archive." >&2
  echo "       The link may have expired, or it may require sign-in." >&2
  echo "       First bytes: $(head -c 100 "$TMP/raw-geodata.zip" | tr -d '\0')" >&2
  exit 1
fi

# A Dropbox *folder* link (/scl/fo/) serves a zip that CONTAINS
# polvik-raw-geodata.zip; a *file* link (/scl/fi/) serves that zip directly.
# Handle either, so the script keeps working if the link is ever re-shared.
if unzip -l "$TMP/raw-geodata.zip" | grep -q 'polvik-raw-geodata\.zip'; then
  echo "Folder link detected; unwrapping the inner archive ..."
  unzip -q -o "$TMP/raw-geodata.zip" 'polvik-raw-geodata.zip' -d "$TMP/outer"
  PAYLOAD="$TMP/outer/polvik-raw-geodata.zip"
else
  PAYLOAD="$TMP/raw-geodata.zip"
fi

echo "Extracting into $DEST ..."
unzip -q -o "$PAYLOAD" -d "$DEST"

verify
