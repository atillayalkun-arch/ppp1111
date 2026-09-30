import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
exec(open('step3_measure.py').read().split('# back wall rectangle')[0])   # reuse L, helpers
M=json.load(open('_m_partial.json'))
xr=sub_fit_vertical(1096,1115,142,250)           # clean segment above the switch/bubble
yb=sub_fit_horizontal(615,632,760,850)           # clean segment right of the character
xr2=sub_fit_vertical(1096,1115,340,430)
print('right wall refit',xr,xr2,' bottom refit',yb)
rw=M['room_lines']['back_wall']; rw['right_x']=round(xr[0],2); rw['right_x_std']=round(xr[1],2); rw['bottom_y']=round(yb[0],2); rw['bottom_y_std']=round(yb[1],2)
# tight bboxes of missing elements from diff vs bg-composite
S='../source/'
comp=np.asarray(Image.open('recomposed.png').convert('RGB')).astype(float); O=np.asarray(Image.open(S+'original.jpg').convert('RGB')).astype(float)
d=np.abs(comp-O).max(axis=2)
def bbox(x0,y0,x1,y1,thr=24):
    m=d[y0:y1,x0:x1]>thr; ys,xs=np.nonzero(m); return [int(xs.min())+x0,int(ys.min())+y0,int(xs.max())+x0+1,int(ys.max())+y0+1]
def tl(b): return {'x':b[0],'y':b[1],'w':b[2]-b[0],'h':b[3]-b[1],'right':b[2],'bottom':b[3]}
miss={'bed':bbox(0,400,600,768),'lamp':bbox(540,0,840,60),'switch':bbox(1140,215,1210,320),
 'label_3_old_regret':bbox(300,45,500,100),'label_2_future_worry':bbox(835,140,1070,192),'label_1_unfinished_today':bbox(1080,432,1340,490)}
M['missing_elements_bbox']={k:tl(v) for k,v in miss.items()}
M['missing_elements_bbox']['bed']['note']='sinir esigi 24; golge/ince kenarlar hafif tasabilir'
M['trace_bubbles_in_assets']={'bubble2_small':[790,400,818,426],'bubble3_small':[604,310,633,338],'bubble1_small':[803,506,830,533],'note':'asetlerin icinde, kenarlari yari saydam; ayrica kesim gerekmez (repo prep.py dot_* olarak ayirmisti)'}
M['canvas']={'width':1376,'height':768}
M['assets_json_verified']=json.load(open('step1_result.json'))
M['glow_and_misc']={'lamp_centre_x':round((miss['lamp'][0]+miss['lamp'][2])/2,1),'note':'lamba govdesi arka planda yok, sadece isik halesi var'}
json.dump(M,open('measurements.json','w'),indent=1,ensure_ascii=False)
for k,v in M['missing_elements_bbox'].items(): print(k,v)
print(json.dumps(M['room_lines'],indent=0)[:1500])
