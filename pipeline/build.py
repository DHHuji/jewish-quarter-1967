"""Build the atlas from the scans + catalogue.

  python3 pipeline/build.py            # all sheets
  python3 pipeline/build.py 0015 0016  # only these (others kept from the previous manifest)

Reads   scans/*.JPG, catalogue/sheets.csv, catalogue/classes.csv, pipeline/sheets.py (processing register)
Writes  docs/layers/*.webp, docs/legends/*.png, docs/manifest.json, docs/reference.geojson,
        georef/*.json (IIIF Georeference / Allmaps annotations), provenance.json (+ copy in docs/)
"""
import os, sys, json, math, csv, hashlib, datetime, platform
import numpy as np, cv2
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); DOCS=f"{ROOT}/docs"
sys.path.insert(0,HERE)
from separate import separate, load, paper_mask, SRC
from georef import merc, inv_merc, lines as ref_lines
from sheets import SHEETS, GROUPS

T={k:np.array(v) for k,v in json.load(open(f"{HERE}/sheet_transforms.json")).items()}   # merc -> sheet px
RES=0.6   # metres (Web Mercator) per output pixel; the sheets are ~1.6 px/m so this keeps their resolution
LANDMARKS=[  # control points used for georeferencing (WGS84) -- from OSM, see landmarks.json / ref_osm.json
 ("Dome of the Rock, centre",31.778017,35.235287),("Citadel (Tower of David), centroid",31.776070,35.228081),
 ("City wall, south-west corner",31.772911,35.2277425),("Temple Mount, south-west corner",31.7756683,35.2346228),
 ("Zion Gate",31.772857,35.229638),("Dung Gate",31.774826,35.234173)]

def read_catalogue():
    sheets={r["sheet"]:r for r in csv.DictReader(open(f"{ROOT}/catalogue/sheets.csv",encoding="utf-8"))}
    classes={(r["sheet"],r["key"]):r for r in csv.DictReader(open(f"{ROOT}/catalogue/classes.csv",encoding="utf-8"))}
    return sheets,classes

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()

def sheet_bounds_merc(num):
    rgb=load(num); pm=paper_mask(rgb); ys,xs=np.nonzero(pm)
    corners=np.array([[xs.min(),ys.min()],[xs.max(),ys.min()],[xs.max(),ys.max()],[xs.min(),ys.max()]],float)
    Minv=np.linalg.inv(np.vstack([T[num],[0,0,1]]))
    m=np.array([(Minv@[x,y,1])[:2] for x,y in corners]); return m.min(0), m.max(0), (xs.min(),ys.min(),xs.max(),ys.max())

def warp(layer,num,X0,Y1,W,Hh):
    A=T[num]@np.array([[RES,0,X0],[0,-RES,Y1],[0,0,1]])
    return cv2.warpAffine(layer,A.astype(np.float64),(W,Hh),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))

def georef_annotation(num,cat,paper_box):
    """IIIF Georeference Extension / Allmaps annotation for one sheet.
    Control points: the six landmarks projected through the fitted transform (for 0013 and 0025 these are the
    hand-placed points; for the other sheets they are derived via image registration to those two)."""
    W,H=int(cat["scan_width_px"]),int(cat["scan_height_px"])
    feats=[]
    for name,lat,lon in LANDMARKS:
        u,v=(T[num]@np.array([*merc(lat,lon),1.0])).tolist()
        if 0<=u<W and 0<=v<H:
            feats.append({"type":"Feature","properties":{"resourceCoords":[round(u,1),round(v,1)]},"geometry":{"type":"Point","coordinates":[lon,lat]}})
    x0,y0,x1,y1=paper_box
    return {"@context":["http://iiif.io/api/extension/georef/1/context.json","http://iiif.io/api/presentation/3/context.json"],
            "id":f"georef/{num}.json","type":"Annotation","motivation":"georeferencing",
            "target":{"type":"SpecificResource",
                      "source":{"id":f"scans/{cat['scan_file']}","type":"Image","format":"image/jpeg","width":W,"height":H},
                      "selector":{"type":"SvgSelector","value":f"<svg width=\"{W}\" height=\"{H}\"><polygon points=\"{x0},{y0} {x1},{y0} {x1},{y1} {x0},{y1}\" /></svg>"}},
            "body":{"type":"FeatureCollection","transformation":{"type":"polynomial","options":{"order":1}},"features":feats}}

PROJECT="jewish-quarter-1967"
def last_updated(relpath):
    """Date a data file last changed: its last git commit date, or today if it has uncommitted changes / no history."""
    import subprocess
    try:
        dirty=subprocess.run(["git","status","--porcelain","--",relpath],cwd=ROOT,capture_output=True,text=True).stdout.strip()
        if dirty: return datetime.date.today().isoformat()
        d=subprocess.run(["git","log","-1","--format=%cs","--",relpath],cwd=ROOT,capture_output=True,text=True).stdout.strip()
        return d or datetime.date.today().isoformat()
    except Exception: return datetime.date.today().isoformat()
def dl_name(content,ext,date): return f"{PROJECT}_{content}_{date}.{ext}"
def write_datapackage(manifest):
    """Frictionless Data package describing every downloadable data file, with provenance-carrying file names."""
    C=manifest["collection"]; today=datetime.date.today().isoformat()
    def res(path,name,content,ext,title,desc,fmt,extra=None):
        d=last_updated(path); r=dict(name=name,path=path,title=title,description=desc,format=fmt,updated=d,download=dl_name(content,ext,d),
                                  bytes=os.path.getsize(f"{ROOT}/{path}") if os.path.exists(f"{ROOT}/{path}") else None)
        if extra: r.update(extra); return r
    sheets_fields=[dict(name=n) for n in next(csv.reader(open(f"{ROOT}/catalogue/sheets.csv",encoding="utf-8")))]
    classes_fields=[dict(name=n) for n in next(csv.reader(open(f"{ROOT}/catalogue/classes.csv",encoding="utf-8")))]
    resources=[
      res("catalogue/sheets.csv","catalogue-sheets","catalogue-sheets","csv","Sheet catalogue","One record per scan (Dublin-Core-shaped): titles as written, transliteration, translation, reading confidence, creator, dates, coverage, relations, rights.","csv",dict(mediatype="text/csv",encoding="utf-8",schema=dict(fields=sheets_fields))),
      res("catalogue/classes.csv","catalogue-classes","catalogue-classes","csv","Legend-class catalogue","One record per legend entry (colour class) on each sheet: legend as written, translation, kind, pigment seed, separation quality, notes.","csv",dict(mediatype="text/csv",encoding="utf-8",schema=dict(fields=classes_fields))),
      res("provenance.json","provenance","provenance","json","Provenance","One PROV-shaped record per derived layer: source scan (sha256), transform, parameters, software, time, agents.","json",dict(mediatype="application/json")),
      res("docs/manifest.json","manifest","atlas-manifest","json","Atlas manifest","Machine-readable catalogue read by the web atlas: sheets, classes, fitted colours, bounds.","json",dict(mediatype="application/json")),
      res("docs/reference.geojson","reference","osm-reference","geojson","Reference geometry","City walls, Temple Mount and landmarks from OpenStreetMap (ODbL), used for georeferencing.","geojson",dict(mediatype="application/geo+json",licenses=[dict(name="ODbL-1.0",title="Open Database License",path="https://opendatacommons.org/licenses/odbl/")])),
    ]
    for s in manifest["sheets"]:
        resources.append(res(f"georef/{s['num']}.json",f"georef-{s['num']}",f"georef-{s['num']}","json",f"Georeference annotation, sheet {s['num']}",f"IIIF Georeference (Allmaps) annotation for {s['identifier']}: control points and paper mask.","json",dict(mediatype="application/json")))
    pkg=dict(name=PROJECT,title=C["title_en"],title_he=C["title_he"],
             description="Ehud Netzer's 1967 planning sheets for the Jewish Quarter of Jerusalem: catalogue, georeferencing, colour-separated layers, provenance.",
             version=today,created="2026-09-18",updated=today,
             homepage="https://dhhuji.github.io/jewish-quarter-1967/",repository="https://github.com/DHHuji/jewish-quarter-1967",
             contributors=[dict(title=C["creator_en"],role="author",path=f"https://www.wikidata.org/wiki/{C['creator_wikidata']}"),dict(title="Yael Netzer",role="maintainer")],
             licenses=[dict(name="see-LICENSE",title=C["rights"]+"; licence "+C["license"])],
             resources=resources)
    json.dump(pkg,open(f"{ROOT}/datapackage.json","w"),ensure_ascii=False,indent=1)
    json.dump(pkg,open(f"{DOCS}/datapackage.json","w"),ensure_ascii=False,indent=1)
    manifest["downloads"]={r["name"]:dict(path=r["path"].replace("docs/",""),download=r["download"],updated=r["updated"]) for r in resources}
    json.dump(manifest,open(f"{DOCS}/manifest.json","w"),ensure_ascii=False,indent=1)
def main(only=None):
    cat,catc=read_catalogue()
    for d in ("layers","legends"): os.makedirs(f"{DOCS}/{d}",exist_ok=True)
    os.makedirs(f"{ROOT}/georef",exist_ok=True)
    nums=[s["num"] for s in SHEETS]
    lo=np.array([np.inf,np.inf]); hi=np.array([-np.inf,-np.inf]); boxes={}
    for n in nums:
        a,b,box=sheet_bounds_merc(n); lo=np.minimum(lo,a); hi=np.maximum(hi,b); boxes[n]=box
    X0,Y0=lo; X1,Y1=hi; W=int(math.ceil((X1-X0)/RES)); Hh=int(math.ceil((Y1-Y0)/RES))
    s_,w_=inv_merc(X0,Y0); n_,e_=inv_merc(X1,Y1); bounds=[[s_,w_],[n_,e_]]
    print(f"frame {W}x{Hh}px  bounds {bounds}")
    any_cat=next(iter(cat.values()))
    manifest=dict(
        collection=dict(title_he="הרובע היהודי 1967 — גיליונות התכנון של אהוד נצר",title_en="The Jewish Quarter, 1967 — Ehud Netzer's planning sheets",
                        creator=any_cat["creator"],creator_en=any_cat["creator_en"],creator_wikidata=any_cat["creator_wikidata"],
                        date_created=any_cat["date_created"],rights=any_cat["rights"],license=any_cat["license"],
                        curator="Yael Netzer",generated=datetime.date.today().isoformat()),
        bounds=bounds,res_m=RES,crs="EPSG:3857 frame; bounds in WGS84 (EPSG:4326)",groups=GROUPS,sheets=[])
    mp=f"{DOCS}/manifest.json"; old={}
    if os.path.exists(mp):
        try: old={s["num"]:s for s in json.load(open(mp))["sheets"]}
        except Exception: old={}
    provp=f"{ROOT}/provenance.json"; prov={"@context":{"prov":"http://www.w3.org/ns/prov#"},"records":[]}
    if os.path.exists(provp):
        try: prov=json.load(open(provp))
        except Exception: pass
    prov["records"]=[r for r in prov["records"] if r["sheet"] not in only] if only else []
    software=dict(python=platform.python_version(),opencv=cv2.__version__,numpy=np.__version__,pipeline="jewish-quarter-1967/pipeline")
    now=datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    for sh in SHEETS:
        num=sh["num"]; c=cat[num]
        if only and num not in only:
            if num in old: manifest["sheets"].append(old[num])
            continue
        print("==",num,c["title_en"])
        classes=[(k[0],k[1],k[2]) for k in sh["classes"]]
        layers,fitted=separate(num,classes,legend_box=sh.get("legend"),**sh.get("params",{}))
        scan_path=f"{SRC}/{c['scan_file']}"; scan_sha=sha256(scan_path)
        entry=dict(num=num,identifier=c["identifier"],group=c["group"],order=int(c["sequence"]),he=c["title_he"],translit=c["title_translit"],en=c["title_en"],
                   confidence=c["title_reading_confidence"],reading_notes=c["reading_notes"],description=c["description_en"],description_he=c["description_he"],
                   coverage_temporal=c["coverage_temporal"],relation=c["relation"],scan=c["scan_file"],scan_size=[int(c["scan_width_px"]),int(c["scan_height_px"])],
                   georef=f"georef/{num}.json",layers=[],classes=[])
        for key,img in layers.items():
            out=warp(img,num,X0,Y1,W,Hh); out[out[...,3]==0,:3]=0
            fn=f"layers/{num}_{key}.webp"; cv2.imwrite(f"{DOCS}/{fn}",cv2.cvtColor(out,cv2.COLOR_RGBA2BGRA),[cv2.IMWRITE_WEBP_QUALITY,88 if key=='scan' else 92])
            entry["layers"].append(dict(key=key,file=fn))
            prov["records"].append({"@id":fn,"@type":"prov:Entity","sheet":num,"class":key,
                "prov:wasDerivedFrom":{"@id":f"scans/{c['scan_file']}","sha256":scan_sha},
                "prov:wasGeneratedBy":{"@type":"prov:Activity","activity":"colour separation + affine warp" if key not in ("scan","base") else ("affine warp" if key=="scan" else "linework separation + affine warp"),
                    "transform_merc_to_pixel":T[num].round(6).tolist(),"frame":{"res_m":RES,"bounds_wgs84":bounds,"size_px":[W,Hh]},
                    "parameters":sh.get("params",{}),"class_seed":dict((k[0],k[1]) for k in sh["classes"]).get(key),"class_fitted":fitted.get(key),
                    "software":software,"prov:endedAtTime":now,
                    "prov:wasAssociatedWith":["Claude (Anthropic) — pipeline author","Yael Netzer — curator"]}})
        for k in sh["classes"]:
            cc=catc.get((num,k[0]),{})
            entry["classes"].append(dict(key=k[0],seed=k[1],color=fitted.get(k[0],k[1]),kind=k[2],he=cc.get("legend_he",k[3]),en=cc.get("legend_en",k[4]),
                                         quality=cc.get("separation_quality",""),notes=cc.get("notes","")))
        if sh.get("legend"):
            x0,y0,x1,y1=sh["legend"]; sc=layers["scan"][y0:y1,x0:x1]
            cv2.imwrite(f"{DOCS}/legends/{num}.png",cv2.cvtColor(sc,cv2.COLOR_RGBA2BGRA)); entry["legend_img"]=f"legends/{num}.png"
        json.dump(georef_annotation(num,c,boxes[num]),open(f"{ROOT}/georef/{num}.json","w"),ensure_ascii=False,indent=1)
        manifest["sheets"].append(entry)
    manifest["sheets"].sort(key=lambda s:s["order"])
    json.dump(manifest,open(mp,"w"),ensure_ascii=False,indent=1)
    json.dump(prov,open(provp,"w"),ensure_ascii=False,indent=1); json.dump(prov,open(f"{DOCS}/provenance.json","w"),ensure_ascii=False,indent=1)
    # copies for the published site (GitHub Pages serves docs/ only)
    import shutil
    for d in ("georef","catalogue"):
        os.makedirs(f"{DOCS}/{d}",exist_ok=True)
        for f in os.listdir(f"{ROOT}/{d}"): shutil.copy(f"{ROOT}/{d}/{f}",f"{DOCS}/{d}/{f}")
    write_datapackage(manifest)
    feats=[dict(type="Feature",properties=dict(name=name,source="OpenStreetMap, ODbL"),geometry=dict(type="LineString",coordinates=[[inv_merc(*p)[1],inv_merc(*p)[0]] for p in pts])) for name,pts in ref_lines]
    json.dump(dict(type="FeatureCollection",features=feats),open(f"{DOCS}/reference.geojson","w"))
    print("done")
if __name__=="__main__": main(sys.argv[1:] or None)
