import json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
S='../source/'
orig=Image.open(S+'original.jpg').convert('RGB'); O=np.asarray(orig).astype(float)
comp=Image.open(S+'background_room.webp').convert('RGBA')
cover=np.zeros(O.shape[:2],bool)
for a in json.load(open('layers_user.json'))['assets'][1:]:
    im=Image.open(S+a['file']).convert('RGBA'); comp.alpha_composite(im,(a['x'],a['y']))
    al=np.zeros(O.shape[:2],bool); al[a['y']:a['y']+im.height,a['x']:a['x']+im.width]=np.asarray(im)[...,3]>8; cover|=al
comp=comp.convert('RGB'); comp.save('recomposed.png')
d=np.abs(np.asarray(comp).astype(float)-O).max(axis=2)
Image.fromarray(np.clip(d*4,0,255).astype(np.uint8)).save('diff_x4.png')
m=ndi.binary_dilation(d>24,iterations=2)
lab,n=ndi.label(m); objs=ndi.find_objects(lab)
rows=[]
for i,s in enumerate(objs,1):
    area=int((lab[s]==i).sum())
    if area<40: continue
    y,x=s; rows.append((area,x.start,y.start,x.stop-x.start,y.stop-y.start,float(d[s][lab[s]==i].mean())))
rows.sort(reverse=True)
for r in rows[:25]: print('area=%d x=%d y=%d w=%d h=%d meandiff=%.1f'%r)
print('mean diff inside asset cover',d[cover].mean(),' outside',d[~cover].mean())
# background blotch: compare bg vs recomposed gradient? measure local std of bg inside asset regions vs smooth
vis=Image.fromarray(np.clip(d*4,0,255).astype(np.uint8)).convert('RGB')
dr=ImageDraw.Draw(vis)
for r in rows[:25]: dr.rectangle([r[1],r[2],r[1]+r[3],r[2]+r[4]],outline=(255,0,0))
vis.save('diff_boxes.png')
