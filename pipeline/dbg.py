import sys; sys.path.insert(0,'.')
import numpy as np, cv2, separate as sp
from sheets import SHEETS
OUT='/tmp/'
def dbg(num,box,params=None):
    sh=[s for s in SHEETS if s['num']==num][0]; classes=[(c[0],c[1],c[2]) for c in sh['classes']]
    p=dict(sh.get('params',{})); p.update(params or {})
    sp.separate(num,classes,legend_box=sh['legend'],**p); D=sp.DEBUG
    x0,y0,x1,y1=box; lab=D['lab'][y0:y1,x0:x1]; ink=D['ink'][y0:y1,x0:x1]
    img=np.full(lab.shape+(3,),255,np.uint8); img[ink&(lab<0)]=(170,170,170)
    for i,c in enumerate(classes): img[lab==i]=sp.hexrgb(c[1])*255
    print(num,{n:int((D['lab']==i).sum()) for i,n in enumerate(D['names'])},'Cb hues',[round(float(np.degrees(np.arctan2(c[1],c[0]))%360)) for c in D['Cb']])
    return np.hstack([sp.load(num)[y0:y1,x0:x1],img])
if __name__=='__main__':
    nums=sys.argv[1:]
    boxes={"0021":(250,500,950,1250),"0028":(250,500,950,1300),"0031":(300,900,900,1500),"0032":(100,550,950,1450),"0017":(300,500,950,1300)}
    tiles=[cv2.resize(dbg(n,boxes[n]),(1600,int(1600*(boxes[n][3]-boxes[n][1])/(2*(boxes[n][2]-boxes[n][0]))))) for n in nums]
    cv2.imwrite(OUT+'dbg_plan.png',cv2.cvtColor(np.vstack(tiles),cv2.COLOR_RGB2BGR))
