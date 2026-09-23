#!/usr/bin/env python3
"""Regenerate country_registry.yaml from the repository contents.

The registry is the join key between the two knowledge graphs. It is generated,
never hand-edited: run this after adding or renaming a country file.

  python3 scripts/build_country_registry.py          # write country_registry.yaml
  python3 scripts/build_country_registry.py --check  # verify it is up to date, exit 1 if not
"""
import datetime
import pathlib
import re
import subprocess
import sys
import unicodedata

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "country_registry.yaml"

# The seven countries the two graphs name differently: people-kg stem -> spatial-kg stem.
# people-kg keeps its original filenames so that existing downstream code still works;
# see docs/COUNTRY_NAMES.md.
OVERRIDE = {
    "CAR": "CentralAfricanRepublic",
    "DRC": "DemocraticRepublicoftheCongo",
    "RepublicofCongo": "RepublicoftheCongo",
    "GuineaBissau": "Guinea-Bissau",
    "IvoryCoast": "CotedIvoire",
    "Eswatini": "Eswatini",
    "SãoToméandPrincipe": "SãoToméandPríncipe",
}

nfc = lambda s: unicodedata.normalize("NFC", s)


def tracked(prefix):
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", prefix],
                         capture_output=True).stdout.decode()
    return [f for f in out.split("\0") if f]


def ascii_key(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)


def collect():
    spatial = {}
    for f in tracked("spatial-kg/CountryFiles"):
        if not f.endswith("Concepts.yaml"):
            continue
        stem = f.split("/")[-1][: -len("Concepts.yaml")]
        doc = yaml.safe_load((ROOT / f).read_text(errors="replace")) or {}
        concepts = [v for v in (doc.get("concepts") or {}).values() if isinstance(v, dict)]
        iso = next((v["iso3c"] for v in concepts if v.get("iso3c")), None)
        if not iso:
            continue
        name = next((v["country_name"] for v in concepts if v.get("country_name")), stem)
        spatial[iso] = (stem, name)

    stem_to_iso = {nfc(s): iso for iso, (s, _) in spatial.items()}
    people = {}
    unmatched = []
    for f in tracked("people-kg/country_files"):
        if not f.endswith("Concepts.yml"):
            continue
        stem = f.split("/")[-1][: -len("Concepts.yml")]
        iso = stem_to_iso.get(nfc(OVERRIDE.get(stem, stem)))
        (people.__setitem__(iso, stem) if iso else unmatched.append(stem))

    display = {}
    cfile = ROOT / "people-kg/country_files/Countries.yml"
    if cfile.exists():
        for line in cfile.read_text(errors="replace").splitlines():
            m = re.search(r"\(countries,\s*(.+?)\)\s*$", line)
            if m:
                display[ascii_key(m.group(1))] = m.group(1).strip()
    return spatial, people, display, unmatched


def render(spatial, people, display):
    def q(s):
        return "null" if s is None else '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    head = f"""# Country registry — the join key between the two knowledge graphs.
#
# Keyed on ISO 3166-1 alpha-3. This file exists because the two graphs, and the
# Countries.yml list, name countries differently, and because people-kg country
# files carry NO country identifier inside them — their filename is the only one.
# Join on `iso3` here rather than on filenames, which differ by design and are
# not guaranteed stable.
#
# Fields
#   name          GADM country_name, read from the spatial-kg concept file
#   spatial_kg    stem in spatial-kg/CountryFiles/ and SettlementCountryFiles/
#                 (append Concepts.yaml / Edges.yaml)
#   people_kg     stem in people-kg/country_files/, or null where the people KG
#                 has no file for this country (append Concepts.yml / Relations.yml)
#   display_name  the spelling used in people-kg/country_files/Countries.yml,
#                 or null if that list has no matching entry
#
# Generated {datetime.date.today()} from the repository itself, not hand-written.
# Regenerate with scripts/build_country_registry.py after adding a country file.

countries:
"""
    lines = [head.rstrip("\n")]
    for iso in sorted(spatial):
        stem, name = spatial[iso]
        disp = display.get(ascii_key(name)) or display.get(ascii_key(stem))
        lines += [f"  {iso}:",
                  f"    name:         {q(name)}",
                  f"    spatial_kg:   {q(stem)}",
                  f"    people_kg:    {q(people.get(iso))}",
                  f"    display_name: {q(disp)}"]
    return "\n".join(lines) + "\n"


def main():
    spatial, people, display, unmatched = collect()
    if unmatched:
        print(f"error: {len(unmatched)} people-kg file(s) match no spatial-kg country: {unmatched}",
              file=sys.stderr)
        print("       add an entry to OVERRIDE in this script.", file=sys.stderr)
        return 1

    text = render(spatial, people, display)
    if "--check" in sys.argv:
        current = OUT.read_text() if OUT.exists() else ""
        # ignore the generation date line, which changes on every run
        strip = lambda s: re.sub(r"^# Generated .*$", "", s, flags=re.M)
        if strip(current) != strip(text):
            print("error: country_registry.yaml is out of date; run "
                  "scripts/build_country_registry.py", file=sys.stderr)
            return 1
        print(f"country_registry.yaml is up to date ({len(spatial)} countries)")
        return 0

    OUT.write_text(text)
    print(f"wrote {OUT.name}: {len(spatial)} countries, {len(people)} with a people-kg file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
