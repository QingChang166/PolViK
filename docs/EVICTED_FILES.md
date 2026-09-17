# Evicted files

Files removed from this repository's working tree and stored in **Dropbox**
instead, to keep the repository clonable. The processed YAML — the actual
knowledge graph — is tracked in git in full and needs nothing from here.

**Nothing listed here is lost.** Every file remains in this repository's git
history and can be restored with `git checkout <commit>~1 -- <path>`, or fetched
from Dropbox with `scripts/fetch_raw_data.sh`.

> **Note on repository size.** Eviction shrinks the *checkout*, not the *clone*.
> Because history is preserved, these blobs stay in `.git` permanently (~165 MB).
> Removing them from history would require rewriting every commit SHA, which was
> rejected — see `docs/CONSOLIDATION.md`, D1.

## Where the files live now

Dropbox: `PolVik/raw-geodata/`, mirroring the paths below.
Retrieve everything with:

```bash
scripts/fetch_raw_data.sh
```

The download is checksum-verified against `scripts/raw_data_manifest.txt`.

---

## Task 3 — spatial-kg (2026-09-17)

Removed in commit `chore: evict raw geodata from spatial-kg`.
**18,046 files, 1.83 GB.** Tracked files under `spatial-kg/` went 19,326 → 1,278;
working tree 2.0 GB → 100 MB.

| Path | Files | Size | What it is | Origin | Regenerable |
|---|---:|---:|---|---|---|
| `spatial-kg/Spatial_Temporal_Object_1990_2014/` | 18,039 | 1,647.4 MB | Historical administrative boundaries, one GeoJSON per country × year × admin level (e.g. `BRA_GAUL2007_ADM2.geojson`), 1990–2014 | **Raw external input** — [SUNGEO](https://www.sungeo.org/) | Re-downloadable from sungeo.org |
| `spatial-kg/Pgc Datasets/` | 6 | 187.7 MB | **Pipeline outputs**, per that folder's own README (retained in the archive): `valid_grid_admin_assignments.gpkg` (grid cells assigned to the largest-overlap valid admin unit), `all_grid_admin_assignments.gpkg` (including non-valid units, for full coverage), `grid_admin_all_levels_intersections.gpkg` (long-format overlaps with area in km² and coverage %), `no_parent_gid.gpkg` (cells assignable to nothing, typically water) | Derived by `spatial-kg/DataPrepare/Function_Admin_GridCell.Rmd` | Yes — re-run the Rmd |
| `spatial-kg/actor_spells_spatial.gpkg` | 1 | 35.3 MB | Actor spells joined to geometry | Derived | Yes |

Note the distillation: the 187.7 MB of `Pgc Datasets` geopackages **produce** the
12.1 MB of `spatial-kg/PgcFiles/*.yaml` that this repository keeps. The YAML is
the result; the geopackages are the scratch work.

### Also removed in the same commit — not geodata, not in Dropbox

| Path | Why |
|---|---|
| `spatial-kg/.gitignore` | Superseded by the root `.gitignore`. The original listed `PolBoundaryKG.Rproj` three times and ignored a `R_Files/` directory that is not present. |
| `spatial-kg/PolBoundaryKG.Rproj` | Per-user RStudio project file; the root `.gitignore` excludes `*.Rproj`. |

---

## Task 4 — people-kg (2026-09-17)

Removed in commit `chore: evict pickled model from people-kg`. **1 file, 13.4 MB.**

| Path | Size | What it is | Why evicted | Regenerable |
|---|---:|---|---|---|
| `people-kg/Aspect_CountVectorizer_model.pkl.zip` | 14,060,307 B (13.4 MB) | Serialized scikit-learn `CountVectorizer`, zipped | Not graph data. Unpickling executes arbitrary code, so nothing in this repository loads it, and it is not needed to read the graph. | Re-trainable from the country files |

**Security note.** Python pickles execute arbitrary code on load. If you retrieve
this file from Dropbox, only unpickle it if you trust its provenance, and never
from an untrusted copy.

---

<!-- Task 5 evictions are appended below. -->
