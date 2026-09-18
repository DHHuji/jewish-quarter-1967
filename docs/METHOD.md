# Method

How the sheets were placed on the map and how the colours were separated. Sheets 0020 and 0024 are duplicate photographs of 0008 and have no layers.

## How the sheets were placed on the map

All sheets share one traced base (city wall, Citadel, Temple Mount edge, Dome of the Rock octagon), drawn with **north to the right** (≈90° clockwise from north‑up).

1. Sheet 0013 was georeferenced by hand against OSM: Dome of the Rock centre, Citadel centroid, the SW wall corner, the Temple Mount SW corner, Zion Gate and Dung Gate. A similarity transform (with reflection, since pixel y points down) fits all six with residuals ≤ 4 px ≈ 2.5 m — the tracing is that accurate.
2. The other 1967 survey sheets were registered to 0013 automatically (SIFT + RANSAC on the shared linework, 375–850 inliers each).
3. The plan sheets (0025, 0027, 0028, 0031, 0032) are on a *different, redrawn base* (the planned blocks). 0025 was georeferenced by hand the same way; the other four were registered to it (376–1004 inliers).
4. Every layer is warped into a north‑up Web Mercator frame at 0.6 m/px (`pipeline/build.py`).

## How the colours were separated (`pipeline/separate.py`)

For each sheet: flatten the paper tone, find ink, then split strokes by **width** (fine pen < 5 px; marker ≥ 5 px; fills ≥ 15 px). Marker pixels are classified against the sheet's legend classes, each seeded from its swatch and refined on that sheet's own pigment (k‑means on parcel cores, so the rims where marker overlaps ink don't vote); the fine‑pen linework colours compete as "base". Classes are declared `fill` or `line` and compete mainly for pixels of their own kind (0015's purple church *outline* vs. the navy Jewish *fills* are nearly the same pigment). A majority vote over each stroke absorbs rims and stipple; tiny components are dropped.

### Reading his palette — the important finding

Across every sheet he uses one warm ramp for "how much": **dark red → orange → yellow**. In the slide scans:

* the **yellow marker, used as a fill, reads as a pale cream wash** (saturation ≈ 0.2, e.g. "1–2 floors", "private Muslim property", "hospital");
* the **orange marker reads as a saturated yellow** (hue ≈ 36–42°, e.g. "2–3 floors", "family waqf", "beit midrash");
* the legend swatches are pressed harder and read redder than the fills they stand for.

So a pale parcel is *not* uncoloured — it is his lightest class. The class seeds in `pipeline/sheets.py` follow this rule.

Known limits: on 0028 the pale‑yellow paths and the tan road bands are not separable in this scan (kept as one class); 0031's outline is the same pen as the hatching and is separated by stroke weight only; cream washes are faint in "as drawn" mode by nature — use "flat colour" to read them.

## Rebuilding

```bash
python3 atlas/build/build.py            # all sheets
python3 atlas/build/build.py 0015 0016  # only some
```

Sheet definitions, legend boxes and per‑sheet parameters are in `pipeline/sheets.py`; georeferencing transforms in `build/sheet_transforms.json`.
