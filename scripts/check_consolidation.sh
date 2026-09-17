#!/usr/bin/env bash
# Verify the consolidation itself: right files present, evicted files absent,
# country names reconciled, both teams' history preserved. Run from the repo root.
#
# This deliberately does NOT validate YAML contents. No file content is edited in
# this repository (see docs/KNOWN_ISSUES.md), so a content validator would only
# block pushes over problems nobody is authorized to repair.
set -uo pipefail

# --final treats a missing folder as a failure rather than "not grafted yet".
# Without it, MISSING is informational, so the check can PASS mid-build.
FINAL=0
[ "${1:-}" = "--final" ] && FINAL=1

cd "$(dirname "${BASH_SOURCE[0]}")/.."
fail=0
note() { printf '  %-9s %s\n' "$1" "$2"; [ "$1" = "FAIL" ] && fail=1; return 0; }
# MISSING is informational mid-build, fatal under --final.
missing() { [ "$FINAL" -eq 1 ] && note FAIL "$1" || note MISSING "$1"; }

echo "== folders =="
for p in spatial-kg people-kg people-kg/localagreement; do
  n=$(git ls-files "$p" | wc -l | tr -d ' ')
  if [ "$n" -gt 0 ]; then note OK "$p: $n tracked files"
  else missing "$p: not present"; fi
done

echo "== evicted paths must not be tracked =="
evicted=$(git ls-files \
  'spatial-kg/Spatial_Temporal_Object_1990_2014/*' \
  'spatial-kg/Pgc Datasets/*' \
  'spatial-kg/actor_spells_spatial.gpkg' \
  'people-kg/Aspect_CountVectorizer_model.pkl.zip' \
  'people-kg/localagreement/*.png' | wc -l | tr -d ' ')
[ "$evicted" -eq 0 ] && note OK "no evicted paths tracked" \
                     || note FAIL "$evicted evicted path(s) still tracked"

echo "== no oversized blobs (GitHub rejects >100MB) =="
big=$(git ls-files -z | xargs -0 -I{} sh -c 'f="{}"; [ -f "$f" ] && [ "$(wc -c <"$f")" -gt 104857600 ] && echo "$f"' 2>/dev/null)
[ -z "$big" ] && note OK "largest tracked file is under 100 MB" \
              || note FAIL "oversized: $big"

echo "== country names reconciled (Task 6) =="
if [ "$(git ls-files people-kg/country_files | wc -l | tr -d ' ')" -gt 0 ]; then
  for old in 'people-kg/country_files/CARConcepts.yml' \
             'people-kg/country_files/DRCConcepts.yml' \
             'people-kg/country_files/RepublicofCongoConcepts.yml' \
             'people-kg/country_files/GuineaBissauConcepts.yml' \
             'people-kg/country_files/IvoryCoastConcepts.yml'; do
    git ls-files --error-unmatch "$old" >/dev/null 2>&1 \
      && note FAIL "old name still present: $old"
  done
  for new in 'people-kg/country_files/CentralAfricanRepublicConcepts.yml' \
             'people-kg/country_files/DemocraticRepublicoftheCongoConcepts.yml' \
             'people-kg/country_files/RepublicoftheCongoConcepts.yml' \
             'people-kg/country_files/Guinea-BissauConcepts.yml' \
             'people-kg/country_files/CotedIvoireConcepts.yml' \
             'people-kg/country_files/EswatiniConcepts.yml'; do
    git ls-files --error-unmatch "$new" >/dev/null 2>&1 \
      || note FAIL "expected renamed file missing: $new"
  done
  for new in 'spatial-kg/CountryFiles/CotedIvoireConcepts.yaml' \
             'spatial-kg/CountryFiles/EswatiniConcepts.yaml'; do
    git ls-files --error-unmatch "$new" >/dev/null 2>&1 \
      || note FAIL "expected renamed file missing: $new"
  done
  # BSD grep has no -P, so do this in python for portability.
  bad=$(git ls-files -z | python3 -c "
import sys
names=[n for n in sys.stdin.buffer.read().decode().split(chr(0)) if n]
print(sum(1 for n in names if chr(39) in n.split('/')[-1]))
")
  [ "${bad:-0}" -eq 0 ] && note OK "no apostrophes in filenames" \
                       || note FAIL "$bad filename(s) contain an apostrophe"
else
  missing "people-kg/country_files absent — rename check skipped"
fi

echo "== history preserved =="
commits=$(git log --oneline 2>/dev/null | wc -l | tr -d ' ')
authors=$(git log --format='%an' 2>/dev/null | sort -u | wc -l | tr -d ' ')
[ "$commits" -gt 50 ] && note OK "$commits commits" \
                      || note FAIL "$commits commits — history looks squashed"
[ "$authors" -gt 1 ] && note OK "$authors distinct authors" \
                     || note FAIL "$authors author — upstream history was lost"

echo
[ "$FINAL" -eq 1 ] && echo "(--final: missing folders count as failures)"
[ "$fail" -eq 0 ] && { echo "PASS"; exit 0; } || { echo "FAIL"; exit 1; }
