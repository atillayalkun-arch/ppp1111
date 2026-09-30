import json, numpy as np
from PIL import Image
S='../source/'
orig=np.asarray(Image.open(S+'original.jpg').convert('RGB')).astype(float)
bg=np.asarray(Image.open(S+'background_room.webp').convert('RGB')).astype(float)
J=json.load(open('layers_user.json'))
H,W=orig.shape[:2]
res={}
def score(arr,x,y,mask_thr=250):
    a=np.asarray(arr); h,w=a.shape[:2]
    x0,y0=max(x,0),max(y,0); x1,y1=min(x+w,W),min(y+h,H)
    sub=a[y0-y:y1-y,x0-x:x1-x]; al=sub[...,3]; m=al>=mask_thr
    if m.sum()==0: return None,0
    o=orig[y0:y1,x0:x1]
    d=np.abs(sub[...,:3].astype(float)-o).mean(axis=2)
    return float(d[m].mean()), int(m.sum())
for a in J['assets']:
    im=Image.open(S+a['file'].replace('background_room.png','background_room.webp')).convert('RGBA')
    assert im.size==(a['width'],a['height']),(a['file'],im.size)
    if a['order']==1: 
        d=np.abs(bg-orig).mean(axis=2); res[a['file']]={'json_mean_diff':float(d.mean()),'note':'tam tuval, nesneler cikarilmis - fark beklenir'}; continue
    base,n=score(im,a['x'],a['y'])
    grid={}
    for dy in range(-4,5):
        for dx in range(-4,5):
            s,_=score(im,a['x']+dx,a['y']+dy); grid[(dx,dy)]=s
    best=min(grid,key=grid.get)
    res[a['file']]={'json_xy':[a['x'],a['y']],'opaque_px':n,'json_mean_diff':round(base,3),
      'best_shift':list(best),'best_xy':[a['x']+best[0],a['y']+best[1]],'best_mean_diff':round(grid[best],3),
      'diff_at_shift_0':round(grid[(0,0)],3)}
json.dump(res,open('step1_result.json','w'),indent=1,ensure_ascii=False)
for k,v in res.items(): print(k,v)
