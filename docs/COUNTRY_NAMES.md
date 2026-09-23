# Country-name reconciliation

The two knowledge graphs named seven countries differently, so joining them by
country required special-casing each one. Reconciled on 2026-09-23 by renaming
twenty files with `git mv`. **No file contents were changed** — the staged diff
showed 20 rename entries and an empty modified-file stat.

Result: `people-kg` country stems with no `spatial-kg` counterpart went **7 -> 0**.

| # | Was (people-kg) | Was (spatial-kg) | Now | Renamed |
|---|---|---|---|---|
| 1 | `CAR` | `CentralAfricanRepublic` | `CentralAfricanRepublic` | 2 people |
| 2 | `DRC` | `DemocraticRepublicoftheCongo` | `DemocraticRepublicoftheCongo` | 2 people |
| 3 | `RepublicofCongo` | `RepublicoftheCongo` | `RepublicoftheCongo` | 2 people |
| 4 | `GuineaBissau` | `Guinea-Bissau` | `Guinea-Bissau` | 2 people |
| 5 | `IvoryCoast` | `Côted'Ivoire` | **`CotedIvoire`** | 2 people + 4 spatial |
| 6 | `Eswatini` | `Swaziland` | **`Eswatini`** | 4 spatial |
| 7 | `SãoToméandPrincipe` | `SãoToméandPríncipe` | `SãoToméandPríncipe` | 2 people |

## Which name won, and why

The default was GADM's spelling: `spatial-kg` derives from GADM and 224 of its
country files already follow it consistently, against seven exceptions in
`people-kg`. Rows 5 and 6 invert that default.

**Row 5, `CotedIvoire`.** GADM's `Côted'Ivoire` contains a non-ASCII `ô` *and* an
apostrophe. The apostrophe breaks unquoted shell globs; the accent is stored
differently by macOS (NFD) and Linux (NFC), so the identical path can fail to match
across machines. Adopting that spelling into `people-kg` would have spread the
defect, so the ASCII form was applied to both graphs instead. This was the only
apostrophe in the repository; there are now none.

**Row 6, `Eswatini`.** The country was renamed from Swaziland in 2018. GADM 2024
still uses the old name and `people-kg` was already correct, so adopting GADM here
would have replaced a current name with an outdated one.

**Row 7 was nearly missed.** `SãoToméandPrincipe` and `SãoToméandPríncipe` differ
by a single character — `i` versus `í` in "Principe". The original mismatch analysis
used a pattern that excluded non-ASCII characters, so this pair was never compared
and the count stood at six until a later audit. A filename mismatch this subtle
would not be caught in review; it would simply fail to join, silently.

## Unicode normalization

All six `SãoToméandPríncipe` filenames are recorded in git as **NFC** — `ã`, `é`
and `í` each a single code point (`U+00E3`, `U+00E9`, `U+00ED`) — identically in
both graphs, verified after renaming. They therefore match byte-for-byte.

Twenty-eight other filenames still carry non-ASCII characters and were left
untouched; see `docs/KNOWN_ISSUES.md` §1 for the list and the fix procedure.

## Consequences

- `spatial-kg` no longer matches GADM's filename convention for Côte d'Ivoire and
  Eswatini. The `iso3c` and `country_name` attributes **inside** those files are
  untouched and still carry GADM's values, so any join on attributes rather than
  filenames is unaffected.
- A future `git subtree pull` from either upstream will re-add the old filenames as
  new files, since upstream never saw these renames. Re-apply this table afterwards.
- Spell-file `locationConceptPath` URLs are unaffected: they address paths in the
  archived source repositories, not in this one.
