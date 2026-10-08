# Consolidation record

Three separately-maintained repositories were merged into this one in September
2026. Full upstream history came across via `git subtree add`, so every original
commit SHA is still addressable here: **1,236 commits by 12 contributors**.

| Folder | Source repository | Grafted from | Role |
|---|---|---|---|
| `spatial-kg/` | `QingChang166/PolBoundaryKG` | `main` @ `cf9e5be` (upstream `825bfbf`) | GADM admin hierarchy, PRIO-GRID mapping, settlements |
| `people-kg/` | `breebangjensen/triad_datacollecting` | `main` @ `e10167b` (upstream `2bbdebd`) | ethnic, linguistic, religious and armed-group ontology |
| `people-kg/localagreement/` | `mervekeskin20/localagreement_visualizations` | `main` @ `48abbf2` (upstream `e3a9a2c`) | local peace agreements, actor spells, analysis notebooks |

## What this consolidation did, and did not, do

**Did:** put three repositories in one place; preserved all three histories and
their authorship; added a README; created `country_registry.yaml` as an explicit
join key between the graphs; normalized two `spatial-kg` filenames; moved 1.85 GB
of geodata to Dropbox so the working tree is ~300 MB instead of ~2.2 GB.

**Did not:** join the two graphs, reconcile concept identifiers, or edit any
file's contents — including files known to be broken. Every graft was verified
byte-identical to its source by SHA-256. See `docs/KNOWN_ISSUES.md`.

## Decisions

- **D8 — restricted geodata purged from history (2026-09-23).** `git rm` leaves
  blobs in the object database, so every clone still carried them. The 18,039
  SUNGEO / FAO GAUL boundary files and the original `gadm41_CAF_2` shapefile set
  were removed from all 1,243 commits with `git filter-repo --invert-paths`.
  FAO GAUL (2015 and earlier editions) forbids redistribution to non-authorized
  users without FAO's written consent, and GADM forbids redistribution without
  prior permission; both were present here as original files with full geometry.

  **Every commit SHA changed.** Authorship, dates, messages and file history are
  intact; only the identifiers differ. A table mapping all 1,243 old SHAs to their
  new ones is kept outside the repository. Seven commits touched only the purged
  paths and no longer exist. `git filter-repo` also rewrote SHA references inside
  commit messages, so the subtree merge commits name the new hashes rather than
  the upstream ones; the table above records both.

  The four `Pgc Datasets/*.gpkg`, `actor_spells_spatial.gpkg` and
  `priogrid_polygons_0.5deg_agreement.geojson` were **kept** in history by
  decision: they are derived products, and PRIO-GRID is open access.
- **D1 — history preserved.** Grafted with `git subtree add`, not rebuilt from zip
  snapshots, which would have produced one commit per repository instead of 1,236.
  `git filter-repo` was initially rejected for size reasons, then applied later for
  licensing reasons — see D8.
- **D2 — processed YAML in git, geodata out.** 18,054 files / 1.85 GB removed from
  the working tree and republished to Dropbox. See `docs/EVICTED_FILES.md` and
  `scripts/fetch_raw_data.sh`. This shrinks the *checkout*, not the *clone* — the
  blobs remain in history, so `.git` is about 180 MB.
- **D3 — two top-level folders.** The agreements layer nests at
  `people-kg/localagreement/`. `git subtree` supports a nested prefix, so its
  history is preserved exactly as for a top-level graft.
- **D4 — join keys untouched.** The 7,626 spell references still address the
  source repositories by URL. See the warning below.
- **D5 — no file-content edits.** Including the unparseable `MaliConcepts.yml`.
  `.gitattributes` performs no line-ending conversion for the same reason.
- **D6 — country naming.** Reconciled through `country_registry.yaml`, keyed on
  ISO 3166-1 alpha-3, rather than by renaming files. `people-kg` filenames are
  unchanged so that code written by the team that built it still works. Only eight
  `spatial-kg` files were renamed. See `docs/COUNTRY_NAMES.md`.
- **D7 — side branches.** `Qing_triad` held only housekeeping commits and was
  ignored. `Summer2024_update` held two files existing nowhere in `main`; their
  contents were copied in, credited to Merve Keskin.

> ## Do not delete the source repositories
>
> D4's deferred join keys resolve **only while the source repositories stay
> readable on GitHub.** Archiving keeps them readable permanently and makes them
> read-only. Deleting any one of them breaks all 7,626 join keys in the graph.
> Do not delete them until those keys have been rewritten.

## Querying history across a subtree graft

`git subtree` preserves commits but does **not** rewrite historical paths. So a
per-file log needs the pre-graft path:

```bash
git log -- spatial-kg/CountryFiles/MaliConcepts.yaml      # 1 commit: the graft
git log --full-history -- CountryFiles/MaliConcepts.yaml  # the real history
```

`git blame` works normally and attributes original authors, as do `git log` and
`git shortlog` across the whole repository.

## Working with the nested subtree

`people-kg/` contains two independent subtrees. A future `git subtree pull` must
name the correct prefix: pulling `triad_datacollecting` into `people-kg` will not
touch `people-kg/localagreement`, and vice versa. Either pull would also re-add
the pre-rename `spatial-kg` filenames, since upstream never saw those renames.

## Contributor identities

Several people appear under more than one git identity — `mervekeskin20` and
`Merve Keskin`; `zhejunq`, `zhejun-qiu` and `Zhejun Qiu`. A `.mailmap` would merge
them in `git shortlog`. Not added, because it maps real people to real addresses
and should be reviewed by those people first.
