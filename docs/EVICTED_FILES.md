# Evicted files

Files removed from this repository's working tree and stored in **Dropbox**
instead, to keep the repository clonable. The processed YAML — the actual
knowledge graph — is tracked in git in full and needs nothing from here.

**Nothing listed here is lost, but recovery differs by file.**

> ### The SUNGEO / FAO GAUL files were removed from git history entirely
>
> On 2026-09-23 the 18,039 `Spatial_Temporal_Object_1990_2014/*.geojson` files and
> the original `gadm41_CAF_2` shapefile set were **purged from every commit** with
> `git filter-repo`, because they are other parties' data redistributed verbatim
> under licences that forbid it (FAO GAUL, GADM). They cannot be recovered from
> this repository by any means. **Dropbox is the only route** — see
> `scripts/fetch_raw_data.sh`, or the pre-rewrite mirror kept outside the repo.
>
> Every other evicted file is still in history and can be restored with
> `git checkout <commit>~1 -- <path>`.

> **Note on repository size.** `git rm` removes a file from the *checkout*, not
> from the *clone*: git keeps every version it has ever tracked, so evicted blobs
> normally stay in `.git` and travel with every clone. That is why the restricted
> geodata had to be purged with `git filter-repo` rather than merely evicted —
> see `docs/CONSOLIDATION.md`, D8. The `.gpkg` files below are still in history by
> deliberate choice and account for most of the remaining ~100 MB pack.

## Totals

| | Files | Size |
|---|---:|---:|
| `spatial-kg` raw and derived geodata | 18,046 | 1,870.4 MB |
| `people-kg` pickled model | 1 | 13.4 MB |
| `people-kg/localagreement` rendered figures | 7 | 12.9 MB |
| **Total** | **18,054** | **1.85 GB** |

## Where the files live now

Dropbox, as a single archive: **`polvik-raw-geodata.zip`** — 469 MB compressed,
1.85 GB expanded, 18,054 files, preserving the `spatial-kg/…` and `people-kg/…`
paths so it extracts straight over a checkout.

```bash
scripts/fetch_raw_data.sh            # download, extract, verify
scripts/fetch_raw_data.sh --verify   # re-check an existing restore, no download
```

Every file is checksum-verified against `scripts/raw_data_manifest.txt`
(18,054 SHA-256 entries). The archive has been round-trip tested: zipped,
extracted to a scratch directory and verified against the manifest, all matching.

The script refuses to run until `DROPBOX_URL` is filled in, and rejects a download
that is not a valid zip — which is what Dropbox returns when a link has expired or
requires sign-in.

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

## Task 5 — people-kg/localagreement (2026-09-17)

Removed in commit `chore: evict rendered figures from the localagreement layer`.
**7 files, 12.9 MB.** The layer goes 29 -> 22 tracked files.

These are rendered output, not data. Each was traced back to the code that draws
it; **two could not be traced**, so "regenerable" is not claimed uniformly.

| File | Size | Regenerable from |
|---|---:|---|
| `network_territorial_competition.png` | 3.4 MB | `ucdp_based_network_visuals.py` |
| `network_spatial_cooccurrence.png` | 2.7 MB | `ucdp_based_network_visuals.py` |
| `network_temporal_control.png` | 2.7 MB | `ucdp_based_network_visuals.py` |
| `splits_car_1314.png` | 2.3 MB | `Mergers_Splits_Snapshots.ipynb`, `multi-layer-split.ipynb` |
| `splits_mergers_car.png` | 0.8 MB | `directed_network_pc.ipynb` |
| `splits_mergers_car_final.png` | 0.8 MB | **not referenced by any script or notebook** |
| `plot_with_edges.png` | 0.1 MB | **not referenced by any script or notebook** |

The last two are the reason the Dropbox copy matters: nothing in this repository
is known to reproduce them. The filename `splits_mergers_car_final.png` suggests a
hand-edited or manually re-run variant of `splits_mergers_car.png`.

### Deliberately kept in git

| Path | Size | Why |
|---|---:|---|
| `priogrid_polygons_0.5deg_agreement.geojson` | 12.8 MB | A processed **input** to the analysis, not rendered output. Under D2 processed data stays in git. |
| `Malispells.yml`, `Carspells.yml` | 1.8 MB | The actor-place-time edges — 1,976 Mali and 1,782 CAR spells. The point of the whole repository. |
| `car_alliance_all.xlsx`, `final_merged_data.csv` | 0.1 MB | Source data for the notebooks. |

---

