# Data model

Four levels of description, each in its own file, each pointing to the one above by identifier.

## 1. Sheet — `catalogue/sheets.csv`

One row per **scan** (16 rows: 13 distinct sheets + 3 duplicate photographs, kept as records and linked by
`relation`). Identifier `JQ1967-NNNN`. Fields, with the Dublin Core term each maps to:

| field | DC term | notes |
|---|---|---|
| `identifier` | `dc:identifier` | `JQ1967-NNNN` |
| `scan_file`, `scan_width_px`, `scan_height_px` | `dc:source` | the file in `scans/` |
| `sheet`, `has_layers`, `group`, `sequence` | — | processing/ordering fields; `has_layers=0` for duplicates |
| `title_he` | `dc:title` (he) | **as written on the sheet** |
| `title_translit`, `title_en` | `dc:title` (he-Latn, en) | |
| `title_reading_confidence` | — | `high` / `medium` / `low`: how sure the transcription is |
| `reading_notes` | — | what is uncertain and why (cropped by the slide mount, unclear word…) |
| `creator`, `creator_en`, `creator_wikidata` | `dc:creator` | אהוד נצר (מנצ'ל); Q573909 |
| `date_created` | `dc:date` | 1967 |
| `coverage_temporal` | `dcterms:temporal` | what the sheet depicts (1967; 1929/1936; before 1948) |
| `coverage_spatial` | `dcterms:spatial` | Jewish Quarter, Old City of Jerusalem; TGN 7002476 |
| `language` | `dc:language` | he |
| `type`, `type_aat` | `dc:type` | plans (drawings), AAT 300011138 |
| `medium`, `support`, `source_format` | `dc:format` | marker + fine-liner; tracing paper (presumed); 35 mm slide → JPEG |
| `description_en`, `description_he` | `dc:description` | |
| `relation` | `dc:relation` | `hasVersion` / `isVersionOf` links between duplicates and between the states of the plan drawing |
| `rights`, `license` | `dc:rights`, `dcterms:license` | |

## 2. Class — `catalogue/classes.csv`

One row per **legend entry** on each sheet (42 rows). Identifier `JQ1967-NNNN/<key>`. Fields: `legend_he` (as written),
`legend_en`, `kind` (`fill` = marker fill, `line` = marker stroke/outline), `pigment_seed` (the colour the separation was
seeded with, as read from the scan), `separation_quality` (`good` / `medium`), `notes` (what the layer does and does not
capture). The fitted pigment colour of the layer actually produced is in `docs/manifest.json` (`classes[].color`).

## 3. Layer — `docs/layers/NNNN_<key>.webp` + `docs/manifest.json`

One georeferenced RGBA raster per class, plus `NNNN_base` (the fine‑pen linework) and `NNNN_scan` (the whole sheet,
vignetting removed). All layers share one frame: Web Mercator (EPSG:3857), 0.6 m/px, bounds in `manifest.json`
(WGS84). `manifest.json` is the machine‑readable catalogue the atlas reads; it is generated from levels 1–2 and the
processing register and should not be edited by hand.

## 4. Georeference — `georef/NNNN.json`

One **IIIF Georeference Extension** annotation per sheet (the format used by [Allmaps](https://allmaps.org)):
the scan as the target image, a polygon mask for the paper area, and ground control points as
`resourceCoords` (pixel) ↔ WGS84 (`geometry`), with a first‑order polynomial transformation. For sheets 0013 and 0025
the points are the hand‑placed ones; for the other sheets they are the same landmarks carried through the
image‑to‑image registration. Residuals ≤ 4 px (≈ 2.5 m) on the two hand‑placed sheets.

## Provenance — `provenance.json`

One record per derived file, PROV‑O‑shaped: `prov:wasDerivedFrom` (scan path + sha256), `prov:wasGeneratedBy`
(activity, the merc→pixel transform, frame, per‑sheet parameters, class seed and fitted colour, software versions,
time), `prov:wasAssociatedWith` (agents). Regenerated on every build.

## Standards this maps onto

* **Dublin Core / DCMI Terms** — sheet level; ingestible by repository software (DSpace, Omeka‑S, Islandora).
* **IIIF Presentation 3 + Web Annotation** — the natural next step: each scan as a Canvas, the legend crop and the
  title transcription as annotations on regions of it; `georef/` already uses the IIIF georeference extension.
* **Getty AAT / TGN, Wikidata** — controlled terms for type, place and creator.
* **W3C PROV‑O** — provenance.
* **GeoJSON / GeoPackage** (future) — when the parcel fabric is vectorised, each parcel carries the sheet‑by‑sheet
  attributes with a `source` field pointing to `JQ1967-NNNN/<key>`.

## What the model cannot express (yet)

The layers are raster: they say *where he used a colour*, not *which parcel* it was. Feature‑level statements
("this building: 3 storeys, Jewish‑owned, destroyed, to be preserved, planned 3 storeys") need the vector step.
