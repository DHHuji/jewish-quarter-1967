"""Write the initial catalogue CSVs (run once; afterwards edit the CSVs directly, not this file)."""
import csv, os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
SCANS=f"{ROOT}/scans"

CREATOR="אהוד נצר (מנצ'ל)"; CREATOR_EN="Ehud Netzer (born Menczel), 1934–2010"; CREATOR_QID="Q573909"
RIGHTS="© Estate of Ehud Netzer; digitised and curated by Yael Netzer"; LICENSE="TBD"

# identifier, sheet, has_layers, group, sequence, title_he, title_translit, title_en, confidence, reading_notes, coverage_temporal, description_en, relation
S=[
("JQ1967-0008","0008",1,"survey",1,"מערכת הדרכים 1967","Ma'arekhet ha-derakhim 1967","Road system, 1967","high","","1967",
 "Roads in and around the Quarter by user: vehicular roads (dark red), main pedestrian routes (orange), secondary pedestrian routes (yellow). Arrows mark the entries from Jaffa Gate and from the Dung Gate road.","hasVersion JQ1967-0020; hasVersion JQ1967-0024"),
("JQ1967-0013","0013",1,"survey",2,"גובה מבנים ברובע (1967)","Govah mivnim ba-rova (1967)","Building heights in the Quarter, 1967","high","","1967",
 "Number of storeys per parcel in 1967: 3–4 (dark red), 2–3 (orange), 1–2 (yellow, applied as a pale wash).",""),
("JQ1967-0014","0014",1,"survey",3,"שטחים פנויים (1967)","Shtahim penuyim (1967)","Vacant areas, 1967","high","","1967",
 "Condition of parcels in 1967: destroyed (orange-red), partly destroyed (yellow), empty (dark teal hatching, including the outline of the area cleared in front of the Western Wall).",""),
("JQ1967-0015","0015",1,"survey",4,"בעלויות לפני ההפקעה","Ba'aluyot lifnei ha-hafka'a","Ownership before the expropriation","high","","1967",
 "Ownership of parcels before the 1968 expropriation: Jewish property (navy), Muslim waqf (red), family Muslim waqf (orange), private Muslim property (yellow wash), church property (purple outline), municipal or government property (green hatching).",""),
("JQ1967-0018","0018",1,"survey",5,"חנויות ובתי מלאכה","Hanuyot u-vatei melakha","Shops and workshops","medium","Second word of the title read as בתי מלאכה; verify against the original.","1967",
 "Commercial frontages: shops and workshops marked in red along the streets, densest along David Street / Street of the Chain and the market streets to the north.",""),
("JQ1967-0016","0016",1,"past",6,"תחום הרובע (בעבר)","Tehum ha-rova (be-avar)","Extent of the Quarter in the past","high","The two dashed boundaries are labelled 1929 (orange) and 1936 (yellow) in the margin; dashed yellow circles east of the Quarter probably mark Jewish holdings outside it.","1929/1936",
 "Former extent of the Jewish Quarter: dashed boundaries for 1929 (orange) and 1936 (yellow); major Jewish institutions as solid dark-brown blocks.",""),
("JQ1967-0019","0019",1,"past",7,"מוסדות יהודיים ברובע (בעבר)","Mosdot yehudiyim ba-rova (be-avar)","Jewish institutions in the Quarter, past","high","Dots inside parcels are not explained in the legend; probably smaller synagogues. The orange loop on the east marks the prayer area at the Western Wall.","before 1948",
 "Former Jewish institutions: synagogues (dark brown), batei midrash (orange), hospitals (yellow wash); dots for smaller institutions; the Western Wall prayer area outlined in orange.",""),
("JQ1967-0021","0021",1,"plan",8,"סכמת התכנון","Skhemat ha-tikhnun","Planning scheme","medium","Title read as סכמת התכנון.","1967",
 "The planning concept: a vehicular ring outside the walls (red, with arrows), pedestrian spines through the Quarter (purple), open squares (blue) and the descent to the Western Wall (dashed navy arrow).",""),
("JQ1967-0017","0017",1,"plan",9,"תכנית שימור","Tokhnit shimur","Preservation plan","high","","1967",
 "Preservation status per building: to preserve (blue outline), to rehabilitate (brown outline), special value (red fill), special façade (navy line).",""),
("JQ1967-0025","0025",1,"plan",10,"תכנון דרכים חדשות","Tikhnun derakhim hadashot","Land use and new roads","medium","Title partly obscured; land-use legend: plan boundary, residential, institutions, hotels and commerce, public institutions, shop frontage, Western Wall plaza. Red fills read as buildings to be removed for the new paths.","1967",
 "Proposed land use on the redrawn block plan, with new paths (yellow) and buildings to be removed for them (red). First state of the drawing reworked in 0028, 0027, 0031 and 0032.","isVersionOf JQ1967-0028; isVersionOf JQ1967-0027; isVersionOf JQ1967-0031; isVersionOf JQ1967-0032"),
("JQ1967-0028","0028",1,"plan",11,"תכנון דרכים","Tikhnun derakhim","Roads plan","high","Yellow paths and pale tan road bands are not separable in this scan and are kept as one layer.","1967",
 "Roads and paths on the land-use plan (yellow and tan) with proposed gardens (green).","isVersionOf JQ1967-0025"),
("JQ1967-0027","0027",1,"plan",12,"גבהים מתוכננים","Gvahim metukhnanim","Planned heights","high","","1967",
 "Planned building heights on the land-use plan: 4 storeys (navy), 3 storeys (red), 1–2 storeys (yellow).","isVersionOf JQ1967-0025"),
("JQ1967-0031","0031",1,"plan",13,'אתר פרויקט "החורבה"','Atar proyekt "ha-Hurva"','The "Hurva" project site',"medium","Title and legend cut by the slide mount; reading of the second line uncertain.","1967",
 "Heavy navy outlines around the compounds of the Hurva square and the blocks south of it, on the land-use plan: the first project site.","isVersionOf JQ1967-0025"),
("JQ1967-0032","0032",1,"plan",14,"תכנון: שלבי ביצוע","Tikhnun: shlavei bitsua","Phasing","low","Title and legend cut by the slide mount; legend entries read as חניון (parking), רכב (vehicle), מסלול כיום (current route).","1967",
 "Phasing / access: parking on the Armenian garden (orange hatching), vehicle routes inside the Quarter (yellow), the current route around the walls (dashed).","isVersionOf JQ1967-0025"),
("JQ1967-0020","0020",0,"survey",1,"מערכת הדרכים 1967","Ma'arekhet ha-derakhim 1967","Road system, 1967 (second photograph)","high","Duplicate photograph of sheet 0008.","1967","Second photograph of the same sheet as 0008.","isVersionOf JQ1967-0008"),
("JQ1967-0024","0024",0,"survey",1,"מערכת הדרכים 1967","Ma'arekhet ha-derakhim 1967","Road system, 1967 (third photograph)","high","Duplicate photograph of sheet 0008.","1967","Third photograph of the same sheet as 0008.","isVersionOf JQ1967-0008"),
]
cols=["identifier","scan_file","scan_width_px","scan_height_px","sheet","has_layers","group","sequence","title_he","title_translit","title_en","title_reading_confidence","reading_notes",
      "creator","creator_en","creator_wikidata","date_created","coverage_temporal","coverage_spatial","language","type","type_aat","medium","support","source_format",
      "description_en","description_he","relation","rights","license"]
with open(f"{ROOT}/catalogue/sheets.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(cols)
    for (idn,num,hl,grp,seq,he,tr,en,conf,notes,cov,desc,rel) in S:
        fn=f"Jewish Quarter Jerusalem{num}.JPG"; W,H=Image.open(f"{SCANS}/{fn}").size
        w.writerow([idn,fn,W,H,num,hl,grp,seq,he,tr,en,conf,notes,CREATOR,CREATOR_EN,CREATOR_QID,"1967",cov,
                    "Jewish Quarter, Old City of Jerusalem (TGN 7002476 Jerusalem)","he","Image; hand-drawn plan","plans (drawings) [AAT 300011138]",
                    "felt-tip marker and fine-liner over a traced base plan","tracing paper (presumed)","35 mm colour slide, scanned to JPEG",
                    desc,"",rel,RIGHTS,LICENSE])

# classes: sheet, key, legend_he (as written), legend_en, kind, pigment_seed, separation_quality, notes
import importlib.util, sys
spec=importlib.util.spec_from_file_location("sheets",f"{HERE}/sheets.py"); sh=importlib.util.module_from_spec(spec); spec.loader.exec_module(sh)
QUAL={("0028","paths"):("medium","Yellow paths and tan road bands merged: not separable in the scan."),
      ("0031","site"):("medium","Same pen as the base hatching; separated by stroke weight only."),
      ("0013","h12"):("good","His yellow marker used as a light fill reads as a pale cream wash."),
      ("0015","muslim_private"):("good","Pale cream wash (his yellow marker)."),
      ("0019","hospital"):("good","Pale cream wash (his yellow marker)."),
      ("0015","church"):("good","Outline stroke; same pigment family as the navy fills, separated by kind (line vs fill)."),
      ("0032","parking"):("medium","Orange hatching; yellow route rims partly attracted to this class."),
      ("0017","facade"):("medium","Thin navy strokes close to the base-pen colour; partly captured."),
      ("0019","kotel_route"):("good","Not in his legend: the orange loop around the Western Wall prayer area.")}
with open(f"{ROOT}/catalogue/classes.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["identifier","sheet","key","legend_he","legend_en","kind","pigment_seed","separation_quality","notes"])
    for s in sh.SHEETS:
        for c in s["classes"]:
            q,n=QUAL.get((s["num"],c[0]),("good",""))
            w.writerow([f"JQ1967-{s['num']}/{c[0]}",s["num"],c[0],c[3],c[4],c[2],c[1],q,n])
print("catalogue written")
