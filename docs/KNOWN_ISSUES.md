# Known issues

Carried over from the source repositories. **None were introduced by
consolidation.** Recorded so they are not rediscovered, and so the deferred ones
can be picked up deliberately rather than stumbled into.

Sections are added as consolidation proceeds; the list is complete at Task 8.

---

## Deferred work — fix list

Every item below was found during consolidation and deliberately **not** fixed,
either because it was out of scope or because it is a content decision for the
project owner. Nothing here is a regression; all of it predates consolidation.

Ordered by what would hurt most if left alone.

| # | Issue | Impact if ignored | Effort | Decision needed first |
|---|---|---|---|---|
| 2 | Spell data duplicated at two spatial resolutions, filenames differing only by case | **Silent double-counting** of every event in any model that globs both files; the PRIO-GRID mapping is easy to miss entirely | Medium | Yes — which file is canonical, and whether to merge them |
| 4 | `people-kg/MaliConcepts.yml` does not parse | Mali is the CSS2026 pilot country and this file is **unreadable to every consumer** | **One line** | No — it is a missing comma |
| 1 | 28 filenames carry non-ASCII characters | Paths can fail to match between macOS (NFD) and Linux (NFC); the gate no longer warns about it | Low, mechanical | No — mapping already written out below |
| 3 | Two `*_actor_agreement_spells.yaml` are exact duplicates across directories | Copies drift the moment one is edited; no marker of which is authoritative | Low | Yes — which copy to delete |
| 5 | Spell join keys still point at the archived source repositories | Graph does not resolve within this repo; **source repos must never be deleted** | High | Yes — target identifier scheme |
| 6 | Two PNGs nothing in the repo can regenerate | Dropbox copy is the only reproduction path | Low | No — either script them or accept |
| 7 | Concept IDs not globally unique in `people-kg` | `fulaEthnicGroup` (Mali) and `fulaniEthnicGroup` (CAR) are one population under two keys | High | Yes — entity-resolution approach |

**Cheapest first pass:** items 4, 1 and 3 need no design decisions and together take
under an hour. Item 2 is the one that will quietly corrupt results if left.

---

## 1. 28 filenames contain non-ASCII characters — deferred, fix later

Twenty-eight tracked files carry accented country names. The spellings are
**correct**; the problem is portability, not orthography.

| Tree | Names |
|---|---|
| `spatial-kg/CountryFiles/` and `SettlementCountryFiles/` | `México`, `Réunion`, `Åland`, `Curaçao`, `Saint-Barthélemy`, `SãoToméandPríncipe` |
| `people-kg/country_files/` | `Réunion`, `SãoToméandPríncipe` |

### Why this is a problem

macOS and Linux store accented characters differently. macOS uses **NFD**, which
writes `é` as `e` followed by a combining accent (two code points). Linux uses
**NFC**, a single code point. The bytes differ, so **the same filename can fail to
match across machines** — a script that finds `RéunionConcepts.yaml` on one
developer's laptop may find nothing on another's, or in CI.

This is the same defect that made `Côted'Ivoire` worth renaming in Task 6. The
apostrophe there added a second problem (it breaks unquoted shell globs), which is
why that one was fixed first.

### Decision

**Left as-is** for now, by decision of the repository owner. Renaming 28 files was
out of scope for consolidation.

Consequently `scripts/check_consolidation.sh` asserts only that no filename
contains an **apostrophe**. It deliberately does **not** flag non-ASCII filenames,
because the strict form could never pass while these 28 exist. **The gate will not
warn you about this.**

### How to fix it when you want to

Rename each to its ASCII form with `git mv`, as Task 6 did for
`Côted'Ivoire` -> `CotedIvoire`:

```
MéxicoConcepts.yaml              -> MexicoConcepts.yaml
RéunionConcepts.yaml             -> ReunionConcepts.yaml
ÅlandConcepts.yaml               -> AlandConcepts.yaml
CuraçaoConcepts.yaml             -> CuracaoConcepts.yaml
Saint-BarthélemyConcepts.yaml    -> Saint-BarthelemyConcepts.yaml
SãoToméandPríncipeConcepts.yaml  -> SaoTomeandPrincipeConcepts.yaml
```

…and the matching `Edges`/`Relations` files in both trees. Then tighten the check
back to rejecting any non-ASCII filename. The `iso3c` and `country_name`
attributes **inside** the files are unaffected either way, so anything joining on
attributes rather than filenames already works.

### Two other awkward filenames

| Path | Problem |
|---|---|
| `people-kg/country_files/country_tracker (4).xlsx` | Spaces and parentheses; the `(4)` is a browser download suffix, suggesting an accidental commit. Not referenced by anything in the repo. |
| `people-kg/wikidata_scripts/wikidata scrape api.py` | Spaces in a Python filename, so it cannot be imported as a module — only run as a script. |

Also left as-is.

---

## 2. The same spells exist twice, at different spatial resolutions

Consolidation placed two versions of the CAR and Mali spell data in sibling
directories, under names that **differ only by one capital letter**:

| | `people-kg/country_files/` | `people-kg/localagreement/` |
|---|---|---|
| CAR | `CarSpells.yml` — 1,825 rows | `Carspells.yml` — 1,782 rows |
| Mali | `MaliSpells.yml` — 2,043 rows | `Malispells.yml` — 1,976 rows |

**They are not competing datasets.** Compared by `(actor, spell_start, spell_end)`
they are identical: 1,641 CAR events and 1,737 Mali events, present in both, with
the same 23 CAR and 25 Mali actors. Nothing is unique to either side.

The difference is **spatial resolution**. `country_files/` carries each event at
several granularities, distinguished by a key suffix; `localagreement/` carries one
row per event, generally at Adm2.

| Suffix in `country_files/` | CAR rows | Mali rows | Resolves to |
|---|---:|---:|---|
| `adm0` | 46 | 236 | country, e.g. `MLI_Adm0` |
| `adm1` | 57 | 89 | region, e.g. `MLI.4_1_Adm1` |
| `adm2` | 153 | 182 | district, e.g. `MLI.9.5_1_Adm2` |
| `grid` | 1,569 | 1,536 | **PRIO-GRID cell**, e.g. `158763Pgc` |

So one event appears as up to four rows:

```
AQIM_01adm0   31-05-2009   MLI_Adm0
AQIM_01adm1   16-06-2009   MLI.4_1_Adm1
AQIM_01adm2   25-11-2011   MLI.9.5_1_Adm2
AQIM_01grid   30-06-2005   158763Pgc
```

Note the key numbering restarts within each suffix, so `AQIM_01adm0` and
`AQIM_01grid` are **different events**, not one event at two levels. Keys cannot be
matched across the two files; match on `(actor, spell_start, spell_end)` instead.

### Why this needs attention

- **Double-counting.** Any code globbing `**/*[Ss]pells.yml` loads both files and
  counts every event two to five times. The near-identical filenames make this easy
  to do by accident.
- **Case-insensitive filesystems.** `CarSpells.yml` and `Carspells.yml` differ only
  in case. They are safe in separate directories, but if the two are ever flattened
  into one folder on macOS or Windows, **one silently overwrites the other**.
- **The grid rows are the useful ones for forecasting.** 1,569 CAR and 1,536 Mali
  spells are already mapped to PRIO-GRID cells, which is the unit most conflict
  forecasting models predict on. That mapping exists only in `country_files/`.

### Not yet decided

Which file is canonical for which purpose, and whether the two should be merged
into one multi-resolution file. No change was made during consolidation.

## 3. Two files are exact byte-for-byte duplicates

| File | Size | Locations |
|---|---:|---|
| `car_actor_agreement_spells.yaml` | 41,296 B | `people-kg/country_files/` and `people-kg/localagreement/` |
| `mal_actor_agreement_spells.yaml` | 27,859 B | `people-kg/country_files/` and `people-kg/localagreement/` |

Identical SHA-256 on both sides. Harmless today, but the two copies will drift the
moment anyone edits one, and there is nothing to indicate which is authoritative.
Left as-is; deleting one is a content decision.

---

<!-- Further sections are appended by Tasks 6-8. -->
