# Country naming across the two graphs

The two knowledge graphs name seven countries differently. They are joined through
**`country_registry.yaml`**, keyed on ISO 3166-1 alpha-3 — not through filenames.

| ISO3 | Country | `spatial-kg` stem | `people-kg` stem |
|---|---|---|---|
| CAF | Central African Republic | `CentralAfricanRepublic` | `CAR` |
| COD | Democratic Republic of the Congo | `DemocraticRepublicoftheCongo` | `DRC` |
| COG | Republic of the Congo | `RepublicoftheCongo` | `RepublicofCongo` |
| GNB | Guinea-Bissau | `Guinea-Bissau` | `GuineaBissau` |
| CIV | Côte d'Ivoire | `CotedIvoire` | `IvoryCoast` |
| SWZ | Eswatini (GADM still says Swaziland) | `Eswatini` | `Eswatini` |
| STP | São Tomé and Príncipe | `SãoToméandPríncipe` | `SãoToméandPrincipe` |

## Why people-kg filenames were left alone

An earlier pass renamed the `people-kg` files to match `spatial-kg`. **That was
reverted**, for three reasons found by inspecting the files:

1. **The filename is the only country identifier people-kg has.** Every
   `spatial-kg` concept carries `iso3c` and `country_name` inside the file, so its
   filename is cosmetic. No `people-kg` country file contains any country field at
   all. Renaming there changes the only identifier those files have.
2. **The concept IDs inside carry the old names** — `IvoryCoastArmedForces`,
   `GuineaBissauSecurityForces`, `tekeEthnicGroup-RepublicofCongo`. Renaming the
   file made the filename disagree with its own contents. Fixing the IDs would be a
   content edit and would break every reference to those concepts.
3. **Existing downstream code depends on the old names.** The people KG was built
   by another team, and 7,626 spell references address concepts as
   `country_files/CARConcepts.yml#/concepts/...`. Renaming would strand that code.

So filenames were the wrong layer to enforce consistency at. There are four
spellings of Côte d'Ivoire in this repository and renaming touches only one:

| Spelling | Where it appears |
|---|---|
| `CotedIvoire` | `spatial-kg` filename (normalized, see below) |
| `IvoryCoast` | `people-kg` filename |
| `Côte d'Ivoire` | `country_name` attribute inside `spatial-kg` files |
| `Côte d’Ivoire` (curly `U+2019`) | `people-kg/country_files/Countries.yml` |

`country_registry.yaml` records all of them against one ISO3 code.

## What *was* renamed: 8 files in spatial-kg

Safe precisely because `spatial-kg` filenames are cosmetic.

| Was | Now | Why |
|---|---|---|
| `Côted'IvoireConcepts.yaml` and `Edges`, in `CountryFiles/` and `SettlementCountryFiles/` | `CotedIvoire…` | Contained a non-ASCII `ô` **and** an apostrophe. Apostrophes break unquoted shell globs; accents are stored as NFD on macOS and NFC on Linux, so the identical path can fail to match across machines. This was the repository's only apostrophe — there are now none. |
| `Swaziland…` (same four positions) | `Eswatini…` | The country was renamed in 2018. GADM 2024 still uses the old label; `people-kg` was already correct. |

The `iso3c` and `country_name` attributes inside those files are untouched and
still carry GADM's values (`SWZ`, `Swaziland`), so the registry maps them correctly.

## Using the registry

```python
import yaml
reg = yaml.safe_load(open("country_registry.yaml"))["countries"]
e = reg["CAF"]
spatial = f"spatial-kg/CountryFiles/{e['spatial_kg']}Concepts.yaml"
people  = f"people-kg/country_files/{e['people_kg']}Concepts.yml"
```

228 countries, 55 of which have a `people-kg` file. The file is **generated, never
hand-edited**:

```bash
python3 scripts/build_country_registry.py          # regenerate
python3 scripts/build_country_registry.py --check  # verify it is current
```

`scripts/check_consolidation.sh` runs `--check` and also verifies that every path
the registry names actually exists.

## One near-miss worth recording

`SãoToméandPrincipe` and `SãoToméandPríncipe` differ by a single character — `i`
versus `í`. The original mismatch analysis used a pattern that excluded non-ASCII
characters, so the pair was never compared and the count stood at six. A filename
mismatch this subtle would not be caught in review; it would simply fail to join,
silently. It is entry `STP` in the registry.

Twenty-eight other filenames still carry non-ASCII characters; see
`docs/KNOWN_ISSUES.md` §1.
