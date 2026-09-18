import cv2, numpy as np
import os
SRC=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"scans")
def load(num): return cv2.cvtColor(cv2.imread(f"{SRC}/Jewish Quarter Jerusalem{num}.JPG"),cv2.COLOR_BGR2RGB)
def paper_mask(rgb):
    g=rgb.mean(2); m=(g>60).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m); i=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    m=(lab==i).astype(np.uint8)
    # fill holes (solid dark marker blocks are darker than the slide border threshold)
    inv=(1-m).astype(np.uint8); n2,lab2,st2,_=cv2.connectedComponentsWithStats(inv)
    h,w=m.shape
    for j in range(1,n2):
        x,y,ww,hh=st2[j,cv2.CC_STAT_LEFT],st2[j,cv2.CC_STAT_TOP],st2[j,cv2.CC_STAT_WIDTH],st2[j,cv2.CC_STAT_HEIGHT]
        if x>0 and y>0 and x+ww<w and y+hh<h: m[lab2==j]=1      # component not touching the image border = hole
    return cv2.erode(m,np.ones((9,9),np.uint8)).astype(bool)
def illumination(rgb,pm):
    f=rgb.astype(np.float32); hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    paperish=pm&(hsv[...,1]<40)&(hsv[...,2]>140); out=np.zeros_like(f)
    for c in range(3):
        ch=f[...,c].copy(); ch[~paperish]=np.nan
        small=cv2.resize(ch,(60,int(60*ch.shape[0]/ch.shape[1])),interpolation=cv2.INTER_AREA)
        small[np.isnan(small)]=np.nanmedian(small)
        for _ in range(3): small=cv2.blur(small,(9,9))
        out[...,c]=cv2.resize(small,(ch.shape[1],ch.shape[0]),interpolation=cv2.INTER_CUBIC)
    return out
DEBUG={}
def hexrgb(h): return np.array([int(h[i:i+2],16) for i in (1,3,5)],np.float32)/255
def feats(h,s,v):
    hr=np.radians(h); return np.stack([np.cos(hr)*1.4,np.sin(hr)*1.4,v*1.2,s*0.5],-1)
def kmeans(F,C,C0=None,drift=None,iters=12,minfrac=0.003):
    for _ in range(iters):
        lab=np.argmin(((F[:,None,:]-C[None,:,:])**2).sum(2),1)
        for i in range(len(C)):
            m=lab==i
            if m.sum()>minfrac*len(lab):
                nc=F[m].mean(0)
                if drift is None or np.linalg.norm(nc-C0[i])<drift: C[i]=nc
    return C,lab
def meanshift(F,C,C0,r=0.35,iters=15):
    C=C.copy()
    for _ in range(iters):
        for i in range(len(C)):
            d2=((F-C[i])**2).sum(1); m=d2<r*r
            if m.sum()>50: C[i]=F[m].mean(0)
    # two seeds that collapsed onto one mode: the one that travelled further goes back to its seed (class absent on this sheet)
    for i in range(len(C)):
        for j in range(i+1,len(C)):
            if np.linalg.norm(C[i]-C[j])<0.08:
                k=i if np.linalg.norm(C[i]-C0[i])>np.linalg.norm(C[j]-C0[j]) else j; C[k]=C0[k]
    return C
def separate(num, classes, legend_box=None, ink_thr=0.12, fill_base_handicap=0.5, wash_sat=0.10, thick_k=5, fill_k=15, thin_sat=0.35, seed_drift=0.60, smooth_k=9, line_base_handicap=0.35, min_area_fill=80, min_area_line=40, thick_from_dark=None):
    """classes: list of (name, hex, kind) kind in {'fill','line'}.  Returns (layers dict, fitted colours)."""
    rgb=load(num); pm=paper_mask(rgb); P=illumination(rgb,pm)
    N=np.clip(rgb.astype(np.float32)/np.maximum(P,1),0,1)
    lum=0.299*N[...,0]+0.587*N[...,1]+0.114*N[...,2]
    hsv=cv2.cvtColor((N*255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32)
    H=hsv[...,0]*2; S=hsv[...,1]/255; V=hsv[...,2]/255
    density=np.clip((1-lum)*1.6+S*0.6,0,1); density[~pm]=0
    ink=density>ink_thr; ink8=ink.astype(np.uint8)
    src8=ink8 if thick_from_dark is None else (ink&(V<thick_from_dark)).astype(np.uint8)   # width measured on solid-dark strokes only
    thick=cv2.morphologyEx(src8,cv2.MORPH_OPEN,np.ones((thick_k,thick_k),np.uint8)).astype(bool)
    fillish=cv2.morphologyEx(src8,cv2.MORPH_OPEN,np.ones((fill_k,fill_k),np.uint8)).astype(bool)
    thin=ink&~thick; lineish=thick&~fillish
    F=feats(H,S,V)
    # linework colours (he used more than one pen): 3 clusters of the thin strokes
    tv=thin&(V<0.85); ty,tx=np.nonzero(tv); ti=np.random.default_rng(1).choice(len(ty),min(40000,len(ty)),replace=False); Ft=F[ty[ti],tx[ti]]
    Cb=Ft[np.random.default_rng(2).choice(len(Ft),3,replace=False)].copy(); Cb,lb=kmeans(Ft,Cb,iters=15)
    Cb=Cb[np.array([(lb==i).sum() for i in range(3)])>0.05*len(lb)]
    bhues=np.degrees(np.arctan2(Cb[:,1],Cb[:,0]))%360
    names=[c[0] for c in classes]; kinds=[c[2] for c in classes]
    cols=np.array([hexrgb(c[1]) for c in classes]); chsv=cv2.cvtColor((cols[None]*255).astype(np.uint8),cv2.COLOR_RGB2HSV)[0].astype(np.float32)
    C=feats(chsv[:,0]*2,chsv[:,1]/255,chsv[:,2]/255); C0=C.copy()
    wash=thick&(S<wash_sat); cand=thick&~wash
    fill_ids=[i for i,k in enumerate(kinds) if k=='fill']; line_ids=[i for i,k in enumerate(kinds) if k=='line']
    both=bool(fill_ids) and bool(line_ids)
    lab=np.full(ink.shape,-1,np.int32)
    def classify(mask, ids, refine, base_handicap=1.0, penal=None, refine_ids=None):
        if not mask.any() or not ids: return
        rid=refine_ids if refine_ids is not None else ids
        if refine and rid:
            core=cv2.erode(mask.astype(np.uint8),np.ones((7,7),np.uint8)).astype(bool)
            if core.sum()<2000: core=mask
            ys,xs=np.nonzero(core); idx=np.random.default_rng(0).choice(len(ys),min(80000,len(ys)),replace=False)
            Fc=F[ys[idx],xs[idx]]
            # refine only the classes of this kind, but let the others (fixed) keep their share of pixels
            allC=C[ids].copy(); fixed=[i for i,g in enumerate(ids) if g not in rid]
            for _ in range(20):
                l=np.argmin(((Fc[:,None,:]-allC[None,:,:])**2).sum(2),1)
                for j,g in enumerate(ids):
                    if j in fixed: continue
                    m=l==j
                    if m.sum()>0.003*len(l):
                        nc=Fc[m].mean(0)
                        if np.linalg.norm(nc-C0[g])<seed_drift: allC[j]=nc
            for j,g in enumerate(ids):
                if j not in fixed: C[g]=allC[j]
        sub=C[ids]
        Fm=F[mask]; dc=((Fm[:,None,:]-sub[None,:,:])**2).sum(2)
        if penal is not None: dc=dc*np.array(penal)[None,:]
        db=((Fm[:,None,:]-Cb[None,:,:])**2).sum(2).min(1)
        l=np.array(ids)[np.argmin(dc,1)]; l=np.where(db<base_handicap*dc.min(1),-1,l); lab[mask]=l
    if both:
        # wide structures: fill classes preferred, line classes allowed with a penalty (very thick dashes / outlines)
        classify(cand&fillish, fill_ids+line_ids, True, base_handicap=fill_base_handicap, penal=[1.0]*len(fill_ids)+[1.8]*len(line_ids), refine_ids=fill_ids)
        # narrow structures: line classes preferred, fill classes allowed with a penalty (small parcels)
        classify(cand&lineish, line_ids+fill_ids, True, base_handicap=line_base_handicap, penal=[1.0]*len(line_ids)+[1.8]*len(fill_ids), refine_ids=line_ids)
    else:
        classify(cand, list(range(len(classes))), True, base_handicap=fill_base_handicap)
    # majority vote among fill-ish pixels: rims where marker overlaps ink take their parcel's class
    for reg,K in ((cand&fillish,int(smooth_k)),(cand&~fillish,max(3,int(smooth_k)-2))):
        if K>1 and reg.any():
            votes=np.stack([cv2.boxFilter(((lab==i)&reg).astype(np.float32),-1,(K,K),normalize=False) for i in range(-1,len(classes))],-1)
            maj=np.argmax(votes,axis=2)-1; lab=np.where(reg,maj,lab)
    # thin strokes: base unless clearly a marker colour far from every linework hue
    hd=np.min(np.abs(((H[...,None]-bhues[None,None,:])+180)%360-180),axis=2)
    tc=thin&(S>thin_sat)&(hd>50)
    if tc.any():
        ids=line_ids if both else list(range(len(classes)))
        if ids:
            d=((F[tc][:,None,:]-C[ids][None,:,:])**2).sum(2); lab[tc]=np.array(ids)[np.argmin(d,1)]
    DEBUG.update(dict(ink=ink,thick=thick,fillish=fillish,thin=thin,wash=wash,cand=cand,lab=lab.copy(),C=C.copy(),Cb=Cb.copy(),H=H,S=S,V=V,names=names))
    a=(density*255).astype(np.uint8); keep=np.ones(ink.shape,bool)
    if legend_box is not None: x0,y0,x1,y1=legend_box; keep[y0:y1,x0:x1]=False
    out={}
    for i,nm in enumerate(names):
        m=(lab==i)&keep; m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        n,cc,st,_=cv2.connectedComponentsWithStats(m,connectivity=8); minA=min_area_fill if kinds[i]=='fill' else min_area_line
        small=np.nonzero(st[:,cv2.CC_STAT_AREA]<minA)[0]; m=m.astype(bool)&~np.isin(cc,small)
        layer=np.zeros((*rgb.shape[:2],4),np.uint8); layer[...,:3]=rgb; layer[...,3]=np.where(m,a,0); out[nm]=layer
    m=ink&(lab<0)&keep; layer=np.zeros((*rgb.shape[:2],4),np.uint8); layer[...,:3]=rgb; layer[...,3]=np.where(m,a,0); out['base']=layer
    tone=np.median(P[pm].reshape(-1,3),0)
    scan=np.zeros((*rgb.shape[:2],4),np.uint8); scan[...,:3]=np.clip(N*tone,0,255).astype(np.uint8); scan[...,3]=np.where(pm,255,0); out['scan']=scan
    fitted={}
    for i,nm in enumerate(names):
        h=np.degrees(np.arctan2(C[i,1],C[i,0]))%360; v=np.clip(C[i,2]/1.2,0,1); s=np.clip(C[i,3]/0.5,0,1)
        r=cv2.cvtColor(np.uint8([[[h/2,s*255,v*255]]]),cv2.COLOR_HSV2RGB)[0,0]; fitted[nm]='#%02x%02x%02x'%tuple(int(x) for x in r)
    return out, fitted
def contact(out,path,cols=4,w=400):
    tiles=[]
    for k,v in out.items():
        im=np.full((*v.shape[:2],3),255,np.uint8); al=v[...,3:4]/255.0
        im=(v[...,:3]*al+im*(1-al)).astype(np.uint8); im=cv2.resize(im,(w,int(w*im.shape[0]/im.shape[1])))
        cv2.putText(im,k,(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2); tiles.append(im)
    rows=[np.hstack(tiles[i:i+cols]) for i in range(0,len(tiles),cols)]
    W=max(r.shape[1] for r in rows); rows=[np.pad(r,((0,0),(0,W-r.shape[1]),(0,0)),constant_values=255) for r in rows]
    cv2.imwrite(path,cv2.cvtColor(np.vstack(rows),cv2.COLOR_RGB2BGR))
if __name__=='__main__':
    out,f=separate("0013",[("h34","#aa3d26","fill"),("h23","#cc6d45","fill"),("h12","#e9bc6f","fill")]); print(f); contact(out,'sep_0013.png',cols=5,w=320)
    out,f=separate("0015",[("jewish","#353668","fill"),("waqf","#b73f24","fill"),("family_waqf","#d6723e","fill"),("muslim_private","#efbd6a","fill"),("church","#5a3f8a","line"),("municipal","#4f6570","fill")]); print(f); contact(out,'sep_0015.png',cols=5,w=320)
