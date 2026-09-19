# Catalogue

Two CSV tables (UTF‑8, comma‑separated, header row). Field definitions: `docs/DATA_MODEL.md`; machine‑readable
schema, licence and last‑updated dates: `datapackage.json` (Frictionless Data).

| file | one row per | identifier |
|---|---|---|
| `sheets.csv` | scan (16: 13 distinct sheets + 3 duplicate photographs) | `JQ1967-NNNN` |
| `classes.csv` | legend entry (colour class) on a sheet (42) | `JQ1967-NNNN/<key>` |

When downloaded from the atlas, the files are named `jewish-quarter-1967_catalogue-sheets_<date>.csv` etc.,
where `<date>` is the date the file last changed in this repository. The same names are listed in
`datapackage.json` → `resources[].download`.

Edit these files directly (a spreadsheet editor or GitHub's web editor); then run `python3 pipeline/build.py`
to regenerate `docs/manifest.json`, `datapackage.json` and the site.
