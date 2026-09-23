# PolViK

Actor–place–time knowledge graphs for conflict forecasting, in one repository.

PolViK models political violence as relationships between **actors**, **places**
and **time** — who was where, when, and in what relation to whom. Both graphs are
plain YAML: concept files declare entities and their attributes, edge files declare
`(parent, child)` relations between concept identifiers.

This repository consolidates three previously separate repositories, preserving
all 1,241 commits and 12 contributors. See `docs/CONSOLIDATION.md`.

## Layout

| Path | Contents | Identifiers look like |
|---|---|---|
| `spatial-kg/` | Administrative hierarchy (GADM admin 0/1/2), PRIO-GRID to admin mappings, human settlements | `MLI.9.5_1_Adm2` |
| `people-kg/` | Ethnic, linguistic, religious, ideological and armed-group ontology | `fulaEthnicGroup` |
| `people-kg/localagreement/` | Local peace agreements, actor spells, analysis notebooks | `al-Murabitun_01` |
| `country_registry.yaml` | **The join key between the two graphs**, on ISO 3166-1 alpha-3 | `CAF`, `MLI` |
| `scripts/` | Consolidation check, registry generator, geodata fetch | |
| `docs/` | Provenance, known issues, country naming, evicted files | |

### `spatial-kg/` — 1,278 files

| Path | Contents |
|---|---|
| `CountryFiles/` | Per-country admin 0/1/2 concepts and edges, from GADM 2024 |
| `PgcFiles/` | PRIO-GRID cells mapped to their lowest-level admin unit |
| `SettlementCountryFiles/` | Human settlements (GUPPD) linked to admin units |
| `GlobalConcepts.yaml`, `GlobalEdges.yaml` | Continents and countries |
| `DataPrepare/` | The R pipeline that regenerates all of the above |

A concept carries `GID` (the original GADM identifier), `admin_name`, `iso3c`,
`country_name` and `admin_level`. An edge file relates a unit to its parent.

### `people-kg/` — 158 files

| Path | Contents |
|---|---|
| `BaseConcepts.yml`, `BaseRelations.yml` | The ontology backbone — the class hierarchy every country file instantiates |
| `country_files/` | Per-country instances: ethnic, linguistic, religious, political and armed groups, for 55 countries |
| `wikidata_scripts/` | Wikidata enrichment helpers |
| `summer2024_updates` | A data-completeness audit of this graph (2024-07-05) |
| `localagreement/` | Local peace agreements in CAR and Mali, actor **spells**, and the notebooks that visualize them |

A concept carries `stringTokens` (surface forms for matching text), usually a
`wikidataQnode`, and type-specific attributes such as `religionsMostPracticed` or
`livesIn`.

**Spells** are the actor–place–time edges: 1,976 for Mali and 1,782 for CAR, each
with `spell_start`, `spell_end`, a location and a group.

## Joining the two graphs

The graphs name seven countries differently, and `people-kg` country files carry
no country field at all — their filename is the only identifier. Join through the
registry, never through filenames:

```python
import yaml
reg = yaml.safe_load(open("country_registry.yaml"))["countries"]

e = reg["CIV"]                                            # Côte d'Ivoire
spatial = f"spatial-kg/CountryFiles/{e['spatial_kg']}Concepts.yaml"   # CotedIvoire…
people  = f"people-kg/country_files/{e['people_kg']}Concepts.yml"     # IvoryCoast…
```

228 countries, 55 with a `people-kg` file. The registry is generated, not
hand-edited — see `docs/COUNTRY_NAMES.md`.

## Quick start

```bash
git clone <this repo> && cd polvik
scripts/check_consolidation.sh --final     # verify the repository is intact
```

Reading the graphs needs only a YAML parser. The R pipeline under
`spatial-kg/DataPrepare/` regenerates the spatial layer from GADM and SUNGEO
sources and is not required to read anything.

```bash
python3 scripts/build_country_registry.py --check   # is the registry current?
```

## Geodata is not in this repository

18,054 files / 1.85 GB of raw SUNGEO historical boundaries, derived PRIO-GRID
geopackages, a trained model and rendered figures live in **Dropbox**, not git, so
the working tree is ~300 MB rather than ~2.2 GB. The processed YAML — the actual
knowledge graph — is tracked here in full and needs nothing from that download.

```bash
scripts/fetch_raw_data.sh            # download (469 MB), extract, verify
scripts/fetch_raw_data.sh --verify   # re-check an existing restore
```

Every file is checksum-verified against `scripts/raw_data_manifest.txt`. Nothing is
lost either way: all of it also remains in this repository's git history. See
`docs/EVICTED_FILES.md`.

## Status

This is a **consolidation** of three repositories, not an integration of them. The
graphs sit side by side and can now be joined by country, but their concept
namespaces remain independent and nothing links an actor to a place automatically.
Several defects were carried across deliberately rather than fixed in transit.

**Read `docs/KNOWN_ISSUES.md` before building on these files.** It opens with a
prioritized fix list. Two items to be aware of immediately:

- The spell data exists twice at different spatial resolutions, under filenames
  differing only by case. Code that globs both will **double-count every event**.
- `people-kg/MaliConcepts.yml` does not parse — a missing comma. Mali is the pilot
  country.

| Document | Covers |
|---|---|
| `docs/KNOWN_ISSUES.md` | Every known defect, with a prioritized fix list |
| `docs/CONSOLIDATION.md` | Provenance, decisions, and why the source repos must not be deleted |
| `docs/COUNTRY_NAMES.md` | How the two graphs name countries, and the registry |
| `docs/EVICTED_FILES.md` | What was moved to Dropbox, and how to get it back |
