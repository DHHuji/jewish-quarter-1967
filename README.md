# הרובע היהודי 1967 — גיליונות התכנון של אהוד נצר
# The Jewish Quarter, 1967 — Ehud Netzer's planning sheets

Thirteen hand‑drawn planning sheets for the Jewish Quarter of the Old City of Jerusalem, drawn by
**אהוד נצר (מנצ'ל) — Ehud Netzer (born Menczel), 1934–2010** ([Wikidata Q573909](https://www.wikidata.org/wiki/Q573909))
in 1967, when he became head architect of the Quarter's restoration. Surveys of the state in 1967
(roads, heights, damage, ownership, shops), memory sheets (the Quarter's former extent and institutions),
and the plan (scheme, preservation, land use, planned heights, the Hurva site, phasing).

This repository holds the scans, a catalogue of them, their georeferencing, the colour‑separated layers
derived from them, the provenance of every derived file, and a web atlas that lays the sheets over
today's city.

**Live atlas:** `https://DHHuji.github.io/jewish-quarter-1967/` (GitHub Pages, from `docs/`).

## Layout

```
scans/          the 16 slide scans as received (JPEG, ~1200×1900 px); the archival originals
catalogue/      sheets.csv  — one record per scan (Dublin‑Core‑shaped; see docs/DATA_MODEL.md)
                classes.csv — one record per legend entry (colour class) on each sheet
georef/         NNNN.json   — one IIIF Georeference (Allmaps) annotation per sheet: control points + image mask
provenance.json one PROV‑style record per derived file: source scan (sha256), transform, parameters, software, time
pipeline/       the derivation: sheets.py (processing register), separate.py (colour separation),
                georef.py + sheet_transforms.json (georeferencing), build.py (writes docs/)
docs/           the published site: index.html, manifest.json, layers/, legends/, tiles/, reference.geojson,
                plus copies of catalogue/ and georef/ so the site can link to them
```

## Rebuild

```bash
pip install numpy opencv-python pillow
python3 pipeline/build.py          # all sheets
python3 pipeline/build.py 0015     # one sheet
python3 -m http.server 8765 --directory docs   # then open http://localhost:8765/
```

`build.py` reads the catalogue CSVs and the processing register, writes the layers, the manifest, the georeference
annotations and the provenance file. Edit descriptions, readings and confidence in `catalogue/*.csv`; edit colour
seeds, legend boxes and separation parameters in `pipeline/sheets.py`.

## How to cite

> Netzer, Ehud (1967). *Planning sheets for the Jewish Quarter, Jerusalem.* Digitised and catalogued by Yael Netzer;
> georeferencing and colour separation pipeline by Yael Netzer with Claude (Anthropic), 2026.
> https://github.com/DHHuji/jewish-quarter-1967

Sheet‑level identifiers are `JQ1967‑NNNN` (NNNN = slide number); class‑level identifiers `JQ1967‑NNNN/<key>`.

## Rights

The drawings are © the estate of Ehud Netzer. Licence for the scans and derived layers: **to be decided**
(recommended: CC BY 4.0 for the layers and catalogue; the scans under the same or CC BY‑NC 4.0).
Code in `pipeline/` and `docs/index.html`: MIT. Base map tiles © OpenStreetMap contributors, ODbL.

See `docs/DATA_MODEL.md` for the data model and the standards it maps to, and `docs/METHOD.md` for how the sheets
were georeferenced and colour‑separated, including what could not be separated.
