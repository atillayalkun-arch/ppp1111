import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
im=Image.open('../source/original.jpg').convert('RGB'); A=np.asarray(im).astype(float); L=A.mean(axis=2)
H,W=L.shape
dark=L<45
M={}
def sub_fit_vertical(x_lo,x_hi,y0,y1):
    # subpixel centre of dark line per row, then median
    xs=[]
    for y in range(y0,y1):
        seg=255-L[y,x_lo:x_hi]; 
        if seg.max()<150: continue
        w=np.clip(seg-seg.max()*0.5,0,None); xs.append(x_lo+(w*np.arange(len(w))).sum()/w.sum()+0.5)
    xs=np.array(xs); return float(np.median(xs)),float(xs.std()),len(xs)
def sub_fit_horizontal(y_lo,y_hi,x0,x1):
    ys=[]
    for x in range(x0,x1):
        seg=255-L[y_lo:y_hi,x]
        if seg.max()<150: continue
        w=np.clip(seg-seg.max()*0.5,0,None); ys.append(y_lo+(w*np.arange(len(w))).sum()/w.sum()+0.5)
    ys=np.array(ys); return float(np.median(ys)),float(ys.std()),len(ys)
# back wall rectangle
xl=sub_fit_vertical(262,284,150,500); xr=sub_fit_vertical(1095,1116,150,480)
yt_l=sub_fit_horizontal(130,146,280,330); yt_r=sub_fit_horizontal(130,146,650,1095)
yb=sub_fit_horizontal(615,632,600,850)
print('left wall x',xl,'right wall x',xr,'top y (left seg)',yt_l,'top y (right seg)',yt_r,'bottom y',yb)
# extents of the dark vertical/horizontal runs
def runs(mask1d):
    idx=np.where(mask1d)[0]
    if len(idx)==0: return []
    br=np.where(np.diff(idx)>3)[0]; st=np.r_[idx[0],idx[br+1]]; en=np.r_[idx[br],idx[-1]]; return list(zip(st.tolist(),en.tolist()))
lx=int(round(xl[0]-0.5)); rx=int(round(xr[0]-0.5))
print('left wall dark y-runs',runs(dark[:,lx]),' right wall y-runs',runs(dark[:,rx]))
ty=int(round(yt_r[0]-0.5)); by=int(round(yb[0]-0.5))
print('top dark x-runs',runs(dark[ty,:]),' bottom dark x-runs',runs(dark[by,:]))
# diagonals: fit lines to dark pixels in regions
def fit_diag(x0,x1,y0,y1):
    m=dark[y0:y1,x0:x1]; ys,xs=np.nonzero(m); xs=xs+x0; ys=ys+y0
    # robust: RANSAC-lite with polyfit x=a*y+b
    best=None
    for _ in range(300):
        i=np.random.choice(len(xs),2,replace=False)
        if ys[i[0]]==ys[i[1]]: continue
        a=(xs[i[0]]-xs[i[1]])/(ys[i[0]]-ys[i[1]]); b=xs[i[0]]-a*ys[i[0]]
        inl=np.abs(xs-(a*ys+b))<1.5
        if best is None or inl.sum()>best[0]: best=(inl.sum(),inl)
    inl=best[1]; a,b=np.polyfit(ys[inl],xs[inl],1); return a,b,int(inl.sum())
np.random.seed(1)
diag={}
for name,box in {'TL':(0,272,0,138),'TR':(1106,1376,0,138),'BR':(1106,1376,640,768),'BL':(0,120,700,768)}.items():
    a,b,n=fit_diag(*box); diag[name]={'x=a*y+b':[round(a,4),round(b,2)],'inliers':n}
    print(name,a,b,n)
# corner points: intersection of diagonal with wall lines
xl_c,xr_c,yt_c,yb_c=xl[0],xr[0],np.mean([yt_l[0],yt_r[0]]),yb[0]
def at_y(n,y): a,b=diag[n]['x=a*y+b']; return a*y+b
corners={'TL':[at_y('TL',yt_c),yt_c],'TR':[at_y('TR',yt_c),yt_c],
         'BR':[at_y('BR',yb_c),yb_c]}
# bottom-left: diagonal meets bottom edge y? use wall x
a,b=diag['BL']['x=a*y+b']; corners['BL_diag_at_y768']=[a*767+b,767]
print('corners',corners)
# diag where they hit canvas top/bottom
M['room_lines']={'back_wall':{'left_x':round(xl_c,2),'right_x':round(xr_c,2),'top_y':round(float(yt_c),2),'bottom_y':round(float(yb_c),2),
   'left_x_std':round(xl[1],2),'right_x_std':round(xr[1],2),
   'left_dark_y_runs':runs(dark[:,lx]),'right_dark_y_runs':runs(dark[:,rx]),
   'top_dark_x_runs':runs(dark[ty,:]),'bottom_dark_x_runs':runs(dark[by,:]),
   'note':'sol/sag duvar dikeyleri ve ust kenar karakter/balonlar yuzunden kesintili; runs gorunen parcalari verir'},
   'corner_diagonals':diag,'corner_points':{k:[round(v[0],1),round(v[1],1)] for k,v in corners.items()},
   'diag_hit_canvas_edges':{}}
for n,(ye) in {'TL':0,'TR':0,'BR':767,'BL':767}.items():
    M['room_lines']['diag_hit_canvas_edges'][n+f'_x_at_y{ye}']=round(at_y(n,ye),1)
# dotted lines
def dots(x0,x1,y0,y1,size=9,thr=18):
    g=ndi.grey_opening(L,size=(size,size)); th=L-g
    sub=th[y0:y1,x0:x1]; m=sub>thr
    lab,n=ndi.label(m); out=[]
    for i in range(1,n+1):
        ys,xs=np.nonzero(lab==i)
        if len(ys)<6 or len(ys)>120: continue
        w=sub[ys,xs]; out.append([round(float((xs*w).sum()/w.sum())+x0+0.5,1),round(float((ys*w).sum()/w.sum())+y0+0.5,1),int(len(ys)),round(float(L[y0:y1,x0:x1][ys,xs].max()),0)])
    out.sort(); return out
d1=dots(640,850,170,250); d2=dots(1030,1080,370,490)
print('arc1',len(d1),d1); print('arc2',len(d2),d2)
M['dotted_lines']={'arc1_upper':{'dots':d1,'fmt':'[cx,cy,area_px,peak_lum]'},'arc2_right':{'dots':d2,'fmt':'[cx,cy,area_px,peak_lum]'}}
json.dump(M,open('_m_partial.json','w'),indent=1)
