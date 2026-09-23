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

DROPBOX_URL="<DROPBOX_DIRECT_URL>"

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

if [ "$DROPBOX_URL" = "<DROPBOX_DIRECT_URL>" ]; then
  cat >&2 <<'MSG'
error: DROPBOX_URL is not set.

  Edit scripts/fetch_raw_data.sh and replace <DROPBOX_DIRECT_URL> with the
  Dropbox share link for polvik-raw-geodata.zip, changing the trailing
  dl=0 to dl=1 so it downloads directly instead of opening a preview page.
MSG
  exit 1
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

echo "Extracting into $DEST ..."
unzip -q -o "$TMP/raw-geodata.zip" -d "$DEST"

verify
