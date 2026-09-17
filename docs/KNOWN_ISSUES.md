# Known issues

Carried over from the source repositories. **None were introduced by
consolidation.** Recorded so they are not rediscovered, and so the deferred ones
can be picked up deliberately rather than stumbled into.

Sections are added as consolidation proceeds; the list is complete at Task 8.

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

<!-- Further sections are appended by Tasks 5-8. -->
