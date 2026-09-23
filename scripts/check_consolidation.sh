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

echo "== purged licence-restricted data must not return =="
# These were removed from ALL history on 2026-09-23 (docs/CONSOLIDATION.md, D8).
# .gitignore cannot stop a merge or `git subtree pull` from reintroducing them,
# so check the index AND the whole object database.
tracked_bad=$(git ls-files -z \
  | python3 -c "
import sys, re
pat = re.compile(r'Spatial_Temporal_Object_1990_2014|gadm41_|_GAUL[0-9]{4}_ADM[0-9]|[.](shp|shx|dbf|prj|cpg)\$')
names = [n for n in sys.stdin.buffer.read().decode().split(chr(0)) if n]
hits = [n for n in names if pat.search(n)]
print(len(hits))
print('\n'.join(hits[:5]))
" )
n_tracked=$(echo "$tracked_bad" | head -1)
[ "${n_tracked:-0}" -eq 0 ] && note OK "no restricted paths tracked" \
  || { note FAIL "$n_tracked restricted path(s) tracked: $(echo "$tracked_bad" | sed -n 2p)"; }

hist_bad=$(git rev-list --objects --all 2>/dev/null \
  | awk '{ $1=""; sub(/^ /,""); if ($0!="") print }' \
  | grep -cE 'Spatial_Temporal_Object_1990_2014|gadm41_|_GAUL[0-9]{4}_ADM[0-9]' || true)
[ "${hist_bad:-0}" -eq 0 ] && note OK "no restricted paths anywhere in history" \
  || note FAIL "$hist_bad restricted object(s) present in history — history is contaminated again"

echo "== no oversized blobs (GitHub rejects >100MB) =="
big=$(git ls-files -z | xargs -0 -I{} sh -c 'f="{}"; [ -f "$f" ] && [ "$(wc -c <"$f")" -gt 104857600 ] && echo "$f"' 2>/dev/null)
[ -z "$big" ] && note OK "largest tracked file is under 100 MB" \
              || note FAIL "oversized: $big"

echo "== country naming (Task 6) =="
if [ "$(git ls-files people-kg/country_files | wc -l | tr -d ' ')" -gt 0 ]; then
  # people-kg keeps its ORIGINAL filenames so existing downstream code still
  # works; the two graphs are joined through country_registry.yaml instead.
  for keep in 'people-kg/country_files/CARConcepts.yml' \
              'people-kg/country_files/DRCConcepts.yml' \
              'people-kg/country_files/RepublicofCongoConcepts.yml' \
              'people-kg/country_files/GuineaBissauConcepts.yml' \
              'people-kg/country_files/IvoryCoastConcepts.yml'; do
    git ls-files --error-unmatch "$keep" >/dev/null 2>&1 \
      || note FAIL "people-kg original name missing: $keep"
  done
  # spatial-kg IS renamed: its filenames are cosmetic (every concept carries iso3c).
  for new in 'spatial-kg/CountryFiles/CotedIvoireConcepts.yaml' \
             'spatial-kg/CountryFiles/EswatiniConcepts.yaml' \
             'spatial-kg/SettlementCountryFiles/CotedIvoireConcepts.yaml' \
             'spatial-kg/SettlementCountryFiles/EswatiniConcepts.yaml'; do
    git ls-files --error-unmatch "$new" >/dev/null 2>&1 \
      || note FAIL "expected renamed file missing: $new"
  done
  bad=$(git ls-files -z | python3 -c "
import sys
names=[n for n in sys.stdin.buffer.read().decode().split(chr(0)) if n]
print(sum(1 for n in names if chr(39) in n.split('/')[-1]))
")
  [ "${bad:-0}" -eq 0 ] && note OK "no apostrophes in filenames" \
                       || note FAIL "$bad filename(s) contain an apostrophe"
else
  missing "people-kg/country_files absent — naming check skipped"
fi

echo "== country registry =="
if [ -f country_registry.yaml ]; then
  python3 scripts/build_country_registry.py --check >/dev/null 2>&1 \
    && note OK "country_registry.yaml is up to date" \
    || note FAIL "country_registry.yaml is stale — run scripts/build_country_registry.py"
  res=$(python3 - <<'PYEOF'
import yaml, pathlib
reg = yaml.safe_load(open("country_registry.yaml"))["countries"]
missing = []
for iso, e in reg.items():
    for base, d, ext in ((e.get("spatial_kg"), "spatial-kg/CountryFiles", ".yaml"),
                         (e.get("people_kg"),  "people-kg/country_files", ".yml")):
        if base and not pathlib.Path(f"{d}/{base}Concepts{ext}").exists():
            missing.append(f"{iso}:{d}/{base}Concepts{ext}")
print(f"{len(reg)} {len(missing)} " + (missing[0] if missing else ""))
PYEOF
)
  set -- $res
  [ "${2:-1}" -eq 0 ] && note OK "$1 entries, every referenced file exists" \
                     || note FAIL "$2 registry entr(y/ies) point at missing files, e.g. ${3:-?}"
else
  missing "country_registry.yaml absent"
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
