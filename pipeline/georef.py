import json, math, sys
import numpy as np
from PIL import Image, ImageDraw
R=6378137.0
def merc(lat,lon): return np.array([R*math.radians(lon), R*math.log(math.tan(math.pi/4+math.radians(lat)/2))])
def inv_merc(x,y): return (math.degrees(2*math.atan(math.exp(y/R))-math.pi/2), math.degrees(x/R))
d=json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'ref_osm.json')))
lines=[]
for e in d['elements']:
    t=e.get('tags',{}); name=t.get('name:en') or t.get('historic') or t.get('barrier') or ''
    if e['type']=='way': lines.append((name,[merc(p['lat'],p['lon']) for p in e['geometry']]))
    else:
        for m in e.get('members',[]):
            if 'geometry' in m: lines.append((name,[merc(p['lat'],p['lon']) for p in m['geometry']]))
wall_pts=np.array([p for n,l in lines if n in('citywalls','city_wall') for p in l])
def nearest_wall(lat,lon):
    q=merc(lat,lon); i=np.argmin(((wall_pts-q)**2).sum(1)); return wall_pts[i]
def fit(pairs, kind='similarity'):
    # pairs: list of (merc_xy, pix_xy). returns 2x3 affine M: pix = M @ [x,y,1]
    A=[];b=[]
    if kind=='similarity':   # similarity WITH reflection (pixel v points down): u=a x + b y + tx ; v = b x - a y + ty
        for (x,y),(u,v) in pairs:
            A.append([x, y,1,0]); b.append(u)
            A.append([-y,x,0,1]); b.append(v)
        p,*_=np.linalg.lstsq(np.array(A),np.array(b),rcond=None)
        a,bb,tx,ty=p; return np.array([[a,bb,tx],[bb,-a,ty]])
    else:
        for (x,y),(u,v) in pairs:
            A.append([x,y,1,0,0,0]); b.append(u)
            A.append([0,0,0,x,y,1]); b.append(v)
        p,*_=np.linalg.lstsq(np.array(A),np.array(b),rcond=None)
        return p.reshape(2,3)
def apply(M,pt): return M@np.array([pt[0],pt[1],1.0])
def overlay(M, img_path, out, pairs=None):
    im=Image.open(img_path).convert('RGB'); dr=ImageDraw.Draw(im)
    for name,l in lines:
        col={'Dome of the Rock':(255,0,0),'Hurva Synagogue':(0,160,0),'Western Wall':(255,140,0),'Temple Mount':(160,0,200),'Tower of David':(0,90,255),'Tiferet Yisrael Synagogue':(0,160,0)}.get(name,(0,200,255))
        pts=[tuple(apply(M,p)) for p in l]
        dr.line(pts,fill=col,width=3)
    if pairs:
        for g,(u,v) in pairs:
            dr.ellipse([u-6,v-6,u+6,v+6],outline=(255,0,255),width=3)
            pu,pv=apply(M,g); dr.ellipse([pu-4,pv-4,pu+4,pv+4],fill=(0,0,0))
    im.save(out)
if __name__=='__main__':
    print('SW corner candidate:', inv_merc(*nearest_wall(31.7727,35.2268)))
