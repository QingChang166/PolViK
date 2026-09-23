# PolViK — Political Violence Knowledge Graph

PolViK encodes **who was where, when, and in what relation to whom**, so that
streams of events on the ground can be used for computational tasks including
**true future forecasting of political violence**.

The project builds and maintains knowledge graphs of spatial-temporal units and
of political-violence-relevant actors across time and space. The graphs are
interconnected data objects recording observations of places, times, actors and
their relations. They do two things at once: organize entities into more and less
general categories, and map observations of actors into spatial-temporal
locations.


---

## At a glance

- **228 countries** of administrative and grid geography; **55** with people data
- **3,758 actor observations** ("spells") in Mali and the Central African Republic
- **1,278 spatial files** (453 concept, 637 edge, 184 grid) and **124 people files** (55 concept, 55 relation), plain YAML throughout
- Nodes cross-referenced to **Wikidata** for further semantic context

---

## The two knowledge graphs

PolViK keeps the spatial-temporal graph and the people knowledge graph as **analytically
distinct objects for organizational purposes**, but they are cross-referenced and
interdependent.

| | `spatial-kg/` | `people-kg/` |
|---|---|---|
| Encodes | places and their nesting | actors and their attributes |
| Node example | `MLI.9.5_1_Adm2` (Tombouctou) | `akanEthnicGroup` |
| Identity comes from | `GID` / `iso3c` inside the file | the filename and concept ID |
| Built from | GADM, PRIO-GRID, SUNGEO, GUPPD | Ethnologue, Joshua Project, UCDP, ACLED, Wikidata |

### Nesting and aggregation

A grid cell in a given month nests within an admin-2 unit in that month, which
nests within admin-1, which nests within a country. There are **multiple
aggregation paths**: the same grid-cell month can roll up to grid-cell quarter,
year, decade, or grid-cell over all time.

```
PRIO-GRID cell (165228Pgc)
  └─ Adm2   MLI.9.5_1_Adm2     Tombouctou
       └─ Adm1   MLI.9_1_Adm1
            └─ Adm0   MLI.0_Adm0    Mali
```

This is why the same actor observation may appear at several resolutions — an
observation is recorded at **the most specific spatial-temporal unit the source
text supports**, and can then be aggregated upward.

### How the graphs connect

When a report says an armed group was active in Kidal in February 2012, that
resolves to nodes in *both* graphs, and is recorded as the actor node being
observed in the most specific spatial-temporal unit available. Those records are
the **spell** files — the cross-reference that makes the two graphs one system.

---

## Quick start

```bash
git clone <this repo> && cd polvik
scripts/check_consolidation.sh --final     # verify the repository is intact
```

Reading the graphs needs only a YAML parser:

```python
import yaml

reg = yaml.safe_load(open("country_registry.yaml"))["countries"]
e = reg["GHA"]

places = yaml.safe_load(
    open(f"spatial-kg/CountryFiles/{e['spatial_kg']}Concepts.yaml"))["concepts"]
actors = yaml.safe_load(
    open(f"people-kg/country_files/{e['people_kg']}Concepts.yml"))["concepts"]

print(places["GHA1.1_2_Adm2"])    # {'GID': 'GHA1.1_2', 'admin_name': 'Asunafo North', ...}
print(actors["akanEthnicGroup"])  # {'stringTokens': ['Akan poeple', 'Akan'], ...}
```

The R pipeline in `spatial-kg/DataPrepare/` regenerates the spatial layer from
GADM and SUNGEO sources. It is not needed to read anything.

---

## Repository structure

| Path | Files | Contents |
|---|---:|---|
| `spatial-kg/CountryFiles/` | 456 | Admin 0/1/2 concepts and edges per country, from GADM |
| `spatial-kg/PgcFiles/` | 368 | PRIO-GRID cells mapped to their lowest admin unit |
| `spatial-kg/SettlementCountryFiles/` | 448 | Human settlements linked to admin units |
| `spatial-kg/Global*.yaml` | 2 | Continents and countries |
| `spatial-kg/DataPrepare/` | 3 | R pipeline that builds the above |
| `people-kg/BaseConcepts.yml`, `BaseRelations.yml` | 2 | Ontology backbone every country file instantiates |
| `people-kg/country_files/` | 124 | 55 concept + 55 relation files, plus spells and helpers |
| `people-kg/wikidata_scripts/` | 4 | Wikidata enrichment helpers |
| `people-kg/localagreement/` | 22 | Local peace agreements, spells, analysis notebooks |
| `country_registry.yaml` | 1 | **The join key between the graphs** |
| `scripts/`, `docs/` | | Tooling and provenance |

---

## The PolViK ontology

Five fundamental classes, plus two secondary ones. The authoritative definition is
the annotation ontology document; this is a summary.

| Class | Meaning |
|---|---|
| **Actor** | Must be political-violence-relevant: armed non-governmental (Wagner Group, MNLA), governmental (Iranian military, US Navy), unarmed non-governmental (Red Cross, MSF), unorganized civilian groupings (Mali civilians), or an individual leader |
| **Location** | Absolute ("Kidal") or relative ("east of the capital") |
| **Time** | Absolute ("February 2012") or relative ("last month"), post-processed to absolute |
| **Event** | PLOVER categories, plus a PolViK-specific `LocatedIn` |
| **Relation** | Whether one actor views another as ally (*positive*), rival (*negative*), or *neutral* |
| *Tools and Techniques* (TaTVP) | Weapons or means used |
| *Source* | Where the information came from |

Actors carry a **role**: `Perpetuator` (caused the action), `Target` (received it),
or `Neutral`.

### Event types

Events use the [PLOVER](http://ploverdata.org/) quad categories:

| Type | PLOVER categories |
|---|---|
| Verbal cooperation | AGREE, CONSULT, SUPPORT, CONCEDE |
| Material cooperation | COOPERATE, AID, RETREAT, INVESTIGATE |
| Verbal conflict | DEMAND, DISAPPROVE, REJECT, THREATEN, SANCTION |
| Material conflict | PROTEST, CRIME, MOBILIZE, COERCE, ASSAULT |
| Located In | PolViK extension, for an actor given a spatial-temporal relation with no explicit event |

---

## Data model

Three file types, all YAML.

### Concept files — the nodes

`spatial-kg/CountryFiles/MaliConcepts.yaml`

```yaml
concepts:
  MLI.9.5_1_Adm2:
    GID: MLI.9.5_1          # original GADM identifier
    admin_name: Tombouctou
    iso3c: MLI
    country_name: Mali
    admin_level: Adm2       # Adm0 country, Adm1 region, Adm2 district
```

`people-kg/country_files/GhanaConcepts.yml`

```yaml
concepts:
  akanEthnicGroup:
    stringTokens: ['Akan poeple', 'Akan']   # surface forms for matching text
    wikidataQnode: ['Q415693']              # cross-reference to Wikidata
    languagesMostSpoken: ['Akan']
    religionsMostPracticed: ['Christianity']
    livesIn: ['Ashanti Region']
```

`stringTokens` is what links free text to a node: an annotator or model matching
"Akan" in a news report resolves it to this concept. (The typo in `'Akan poeple'`
is in the source data and is reproduced here verbatim.)

Grid-cell concepts in `PgcFiles/` carry the admin unit they fall within:

```yaml
concepts:
  165228Pgc:
    GID: MLI.9.5_1
    conceptID: MLI.9.5_1_Adm2    # the admin node this cell nests inside
    admin_name: Tombouctou
    country: MLI
```

### Edge files — the relations

Edges are `(parent, child)` pairs. Spatial edges express nesting; people edges
express class membership.

```yaml
# spatial-kg/CountryFiles/MaliEdges.yaml
relations:
    - (MLI.0_Adm0, MLI.1_1_Adm1)
    - (MLI.1_1_Adm1, MLI.1.1_1_Adm2)

# people-kg/country_files/CARRelations.yml
relations:
  - (EthnicGroup, sangoEthnicGroup)
  - (LinguisticGroup, bandalindaLinguisticGroup)
```

### Spell files — actors observed in space and time

The cross-reference between the graphs. 1,976 for Mali, 1,782 for CAR.

```yaml
al-Murabitun_01:
  spell_start:         [07-10-2013]
  spell_end:           [07-10-2013]
  locationConceptPath: [...MaliConcepts.yaml#/concepts/MLI.2.3_1_Adm2]
  GroupConceptPath:    [...MaliConcepts.yml#/concepts/murabitunArmedNonGovernmentalOrganizedGroup]
  SourceOfInfo:        [UCDP]
  DateOfInfo:          ['Jan 18, 2026, 18:32pm']
  coder:               [Zhejun]
```

Spells in `people-kg/country_files/` carry a resolution suffix — `adm0`, `adm1`,
`adm2` or `grid` — recording the same observation at different aggregation levels.

---

## Joining the two graphs

The graphs name seven countries differently, and **people files carry no country
field** — their filename is the only country identifier. Join on ISO 3166-1
alpha-3 through the registry, never on filenames:

```python
reg = yaml.safe_load(open("country_registry.yaml"))["countries"]
e = reg["CIV"]                                             # Côte d'Ivoire
f"spatial-kg/CountryFiles/{e['spatial_kg']}Concepts.yaml"  # CotedIvoire…
f"people-kg/country_files/{e['people_kg']}Concepts.yml"    # IvoryCoast…
```

228 entries, 55 with a people file. Generated, never hand-edited:

```bash
python3 scripts/build_country_registry.py          # regenerate
python3 scripts/build_country_registry.py --check  # verify it is current
```

**The second join axis is Wikidata.** Most people concepts carry a `wikidataQnode`,
which links them to external semantic context and — where two concepts share a
Q-number — to each other. See `docs/COUNTRY_NAMES.md`.

---

## What is not in this repository

Some files were removed to keep the repository small, and some because their
licences do not permit redistribution. Nothing is lost — this is where each lives.

| Not here | Size | Where to get it |
|---|---:|---|
| `Spatial_Temporal_Object_1990_2014/` — historical administrative boundaries, 18,039 files | 1.65 GB | **Dropbox only.** Also re-downloadable from [SUNGEO](https://www.sungeo.org/) |
| `gadm41_CAF_2.*` — original GADM shapefile | 0.35 MB | **Dropbox only.** Also re-downloadable from [GADM](https://gadm.org) |
| `Pgc Datasets/*.gpkg` — grid-to-admin assignment outputs | 188 MB | Dropbox, or regenerate with `spatial-kg/DataPrepare/Function_Admin_GridCell.Rmd` |
| `actor_spells_spatial.gpkg` — spells joined to geometry | 35 MB | Dropbox, or regenerate |
| `Aspect_CountVectorizer_model.pkl.zip` — trained model | 13 MB | Dropbox. Unpickling executes arbitrary code; load only if you trust the copy |
| `localagreement/*.png` — rendered figures, 7 files | 13 MB | Dropbox, or regenerate from `ucdp_based_network_visuals.py` and the notebooks. Two of the seven are not reproducible by any script here |

The first two rows are **the only route** — they were removed from git history
entirely, because FAO GAUL and GADM forbid redistribution. The rest remain in
history and can also be recovered with `git checkout <commit>~1 -- <path>`.

```bash
scripts/fetch_raw_data.sh            # download (469 MB), extract, verify
scripts/fetch_raw_data.sh --verify   # re-check an existing restore
```

Every file is checksum-verified against `scripts/raw_data_manifest.txt`
(18,054 SHA-256 entries). Full detail: `docs/EVICTED_FILES.md`.

**None of it is needed to read the graphs.** The processed YAML is tracked here in
full; the files above are raw inputs, intermediate products and rendered output.

---

## Reproducing and contributing

| Task | How |
|---|---|
| Verify the repository | `scripts/check_consolidation.sh --final` |
| Regenerate the registry | `python3 scripts/build_country_registry.py` |
| Rebuild the spatial layer | `spatial-kg/DataPrepare/GeoBoundaryProcess.Rmd` (GADM) and `Function_Admin_GridCell.Rmd` (PRIO-GRID) |
| Add a country | Add `<Name>Concepts.yml` and `<Name>Relations.yml` to `people-kg/country_files/`, then regenerate the registry |

Run `scripts/check_consolidation.sh` before committing; it verifies file counts,
that evicted paths stay evicted, that no blob exceeds GitHub's 100 MB limit, and
that the registry is current and every path it names exists.

Provenance and the decisions behind this layout: `docs/CONSOLIDATION.md`.

---

## Data sources

| Source | Feeds | Licence |
|---|---|---|
| [GADM](https://gadm.org) | Administrative boundaries, `GID`, `iso3c` | Academic / non-commercial; **redistribution requires permission** |
| [PRIO-GRID](https://grid.prio.org) | 0.5° grid cells | Open |
| [SUNGEO](https://www.sungeo.org) | Historical boundaries 1990–2014 | Open |
| [GUPPD / SEDAC](https://sedac.ciesin.columbia.edu/data/set/urbanspatial-guppd-v1) | Human settlements | Open (EOSDIS) |
| [UCDP](https://ucdp.uu.se) | Actor spells, events | CC BY 4.0 |
| [ACLED](https://acleddata.com) | Armed-group data | Attribution policy + EULA |
| [Ethnologue](https://www.ethnologue.com) | Ethnic and linguistic groups | **Licensed; redistribution requires SIL permission** |
| [Joshua Project](https://joshuaproject.net) | Ethnic groups, religions | Non-commercial; attribution required |
| [Wikidata](https://www.wikidata.org) | Q-number cross-references | CC0 |
| [PLOVER](http://ploverdata.org/) | Event ontology | Open |

Also: CIA World Factbook, World Directory of Minorities and Indigenous Peoples,
Wikipedia, and the Armed Group Dataset.

---

## Licence

All rights reserved. See [`LICENSE`](LICENSE).

Redistribution is not permitted. Several upstream sources — GADM, Ethnologue and
Joshua Project among them — restrict it, and this repository's terms reflect that.

---

## Citation

If you use PolViK, please cite this repository **and** the upstream sources you
rely on.

**GADM** — Global Administrative Areas (2024). *GADM database of Global
Administrative Areas*. University of California, Berkeley. https://gadm.org

**PRIO-GRID** — Tollefsen, Andreas Forø, Håvard Strand & Halvard Buhaug (2012).
PRIO-GRID: A unified spatial data structure. *Journal of Peace Research* 49(2):
363–374. https://doi.org/10.1177/0022343311431287

**SUNGEO** — Kollman, Ken & Yuri M. Zhukov (2023). *Subnational Geospatial Data
Archive (SUNGEO)*. Ann Arbor, MI: Center for Political Studies, University of
Michigan. https://www.sungeo.org — method: Zhukov, Yuri M., Jason Byers, Marty
Davidson & Ken Kollman (2024). Integrating Data Across Misaligned Spatial Units.
*Political Analysis* 32(1): 17–33.

**GUPPD** — Center for International Earth Science Information Network (CIESIN),
Columbia University & Joint Research Centre (JRC), European Commission (2024).
*Global Urban Polygons and Points Dataset (GUPPD), Version 1* (v1.00) [Data set].
Palisades, NY: NASA Socioeconomic Data and Applications Center (SEDAC).
https://doi.org/10.7927/BRQ1-XC29

**UCDP** — Davies, Shawn, Therése Pettersson & Magnus Öberg (2026). Organized
violence 1989–2025, and violent political protests. *Journal of Peace Research*.
https://doi.org/10.1093/jopres/xjag046 — and Sundberg, Ralph & Erik Melander
(2013). Introducing the UCDP Georeferenced Event Dataset. *Journal of Peace
Research* 50(4): 523–532. https://doi.org/10.1177/0022343313484347

**ACLED** — Raleigh, Clionadh, Roudabeh Kishi & Andrew Linke (2023). Political
instability patterns are obscured by conflict dataset scope conditions, sources,
and coding choices. *Humanities and Social Sciences Communications* 10: 74.
https://doi.org/10.1057/s41599-023-01559-4

**PLOVER** — Halterman, Andy, Philip A. Schrodt, Andreas Beger, Benjamin E.
Bagozzi & Grace I. Scarborough (2023). PLOVER and POLECAT: A New Political Event
Ontology and Dataset. *International Studies Association 2023*.
https://osf.io/preprints/socarxiv/rm5dw

**Ethnologue** — Eberhard, David M., Gary F. Simons & Charles D. Fennig (eds.)
(2025). *Ethnologue: Languages of the World*. Twenty-eighth edition. Dallas, TX:
SIL International. https://www.ethnologue.com

**Joshua Project** — Joshua Project. *Global Peoples Dataset*.
https://joshuaproject.net — data provided by Joshua Project.

**Wikidata** — Wikidata contributors. *Wikidata: a free collaborative knowledge
base*. Wikimedia Foundation. CC0. https://www.wikidata.org

---

## Acknowledgments

We thank the following contributors:

- Qing Chang
- Laura Chelidonopoulos
- João Correa
- Merve Keskin
- Zhejun Qiu

Principal Investigator: **Michael Colaresi**
