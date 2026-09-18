import json, cv2, numpy as np, sys, os
ROOT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'docs'); os.chdir(ROOT)
m=json.load(open('manifest.json')); rows=[]
crop=(250,150,1750,1450)
for s in m['sheets']:
    tiles=[]
    for ly in s['layers']:
        if ly['key']=='scan': continue
        im=cv2.imread(ly['file'],cv2.IMREAD_UNCHANGED); x0,y0,x1,y1=crop; im=im[y0:y1,x0:x1]
        bg=np.full(im.shape[:2]+(3,),255,np.uint8); a=im[...,3:4]/255.0; t=(im[...,:3]*a+bg*(1-a)).astype(np.uint8)
        t=cv2.resize(t,(230,200)); cv2.putText(t,ly['key'],(4,16),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1); tiles.append(t)
    while len(tiles)<7: tiles.append(np.full((200,230,3),255,np.uint8))
    row=np.hstack(tiles); cv2.putText(row,s['num']+' '+s['en'],(4,195),cv2.FONT_HERSHEY_SIMPLEX,0.45,(120,0,0),1); rows.append(row)
out=sys.argv[1] if len(sys.argv)>1 else '/tmp/contact'
cv2.imwrite(out+'_a.png',np.vstack(rows[:7])); cv2.imwrite(out+'_b.png',np.vstack(rows[7:])); print('ok')
