"""Ön hazırlık: temiz arka plan + eksik katmanlar + iz balonlarının ayrılması.

Girdi : source/  (orijinal görsel, kullanıcının asetleri)
Çıktı : assets/  (katman PNG'leri, clean background, layers.json)
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "source", ROOT / "assets"
OUT.mkdir(exist_ok=True)
W, H = 1376, 768

O = np.asarray(Image.open(SRC / "original.jpg").convert("RGB")).astype(np.float32)
B = np.asarray(Image.open(SRC / "background_room.webp").convert("RGB")).astype(np.float32)

GIVEN = {  # kullanıcının JSON'u
    "bubble_2_future_worry": (777, 190),
    "bubble_3_old_regret": (313, 89),
    "bubble_1_unfinished_today": (805, 462),
    "character": (593, 332),
}


def canvas_alpha(img, x, y):
    a = np.zeros((H, W), np.float32)
    a[y:y + img.shape[0], x:x + img.shape[1]] = img[..., 3] / 255.0
    return a


# ---------------------------------------------------------------- oda geometrisi
def line_y(p, q, x):
    return p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0])


TL, TR, BL, BR = (272, 138), (1105, 138), (272, 624), (1105, 624)
LINES = [  # (p, q, kalınlık)
    ((51.6, 0), TL, 3.4), ((1326, 0), TR, 3.4),
    (TL, TR, 3.0), (TL, BL, 3.0), (TR, BR, 3.0), (BL, BR, 3.0),
    (BR, (1331, 768), 3.6), (BL, (40, 763.5), 3.6),
]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
back = (xx >= TL[0]) & (xx <= TR[0]) & (yy >= TL[1]) & (yy <= BL[1])
# tavan: iki köşegenin üstünde kalan bölge
lt = line_y((51.6, 0), TL, xx)
rt = line_y((1326, 0), TR, xx)
ceil = (yy < TL[1]) & (yy < np.where(xx < 689, lt, rt)) | ((yy < TL[1]) & (xx >= TL[0]) & (xx <= TR[0]))
lb = line_y(BL, (40, 763.5), xx)
rb = line_y(BR, (1331, 768), xx)
floor = (yy > BL[1]) & (yy > np.where(xx < 689, lb, rb)) | ((yy > BL[1]) & (xx >= TL[0]) & (xx <= TR[0]))
left = (xx < TL[0]) & ~ceil & ~floor
right = (xx > TR[0]) & ~ceil & ~floor
PLANES = {"ceiling": ceil & ~back, "back": back, "floor": floor & ~back, "left": left, "right": right}

# ---------------------------------------------------------------- nesne maskeleri
layers = {}
given_alpha = {}
for name, (x, y) in GIVEN.items():
    img = np.asarray(Image.open(SRC / f"{name}.png").convert("RGBA"))
    given_alpha[name] = canvas_alpha(img, x, y)

diff = np.abs(O - B).mean(2)
assets_any = np.maximum.reduce(list(given_alpha.values())) > 0.02


def region_mask(box, thr=22, dilate=2, keep_largest=True, hull=False):
    x0, y0, x1, y1 = box
    m = np.zeros((H, W), np.uint8)
    sub = (diff[y0:y1, x0:x1] > thr) & ~assets_any[y0:y1, x0:x1]
    if hull:  # açık, doygunluğu düşük piksel (etiket hapı) de nesneye aittir
        o = O[y0:y1, x0:x1]
        lum, sat = o.mean(2), (o.max(2) - o.min(2)) / (o.max(2) + 1)
        sub |= (lum > 205) & (sat < 0.1) & ~assets_any[y0:y1, x0:x1]
    m[y0:y1, x0:x1] = sub.astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    if keep_largest and n > 1:
        k = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        m = (lab == k).astype(np.uint8) * 255
    if hull:
        pts = cv2.findNonZero(m)
        m = np.zeros((H, W), np.uint8)
        cv2.fillConvexPoly(m, cv2.convexHull(pts), 255)
    # delikleri doldur
    ff = m.copy()
    cv2.floodFill(ff, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 255)
    m = m | cv2.bitwise_not(ff)
    if dilate:
        m = cv2.dilate(m, np.ones((dilate * 2 + 1, dilate * 2 + 1), np.uint8))
    return m > 0


EXTRA = {
    "bed": ((60, 420, 612, 768), 22, 3, True, False),
    "lamp": ((555, 0, 822, 52), 14, 2, True, True),
    "switch": ((1148, 222, 1198, 312), 18, 2, True, True),
    "label_3_old_regret": ((300, 50, 505, 97), 999, 3, False, True),
    "label_2_future_worry": ((838, 146, 1063, 192), 999, 3, False, True),
    "label_1_unfinished_today": ((1082, 438, 1336, 486), 999, 3, False, True),
}
extra_masks = {k: region_mask(*v) for k, v in EXTRA.items()}

# noktalı çizginin ışık izi
DOTS = [[1059, 464], [1061, 451], [1061, 437], [1060, 424], [1058, 411], [1054, 399], [1050, 388],
        [808, 229], [798, 225], [789, 219], [779, 215], [768, 210], [757, 206], [747, 204], [736, 201],
        [725, 198], [714, 196], [703, 195], [692, 194], [680, 194], [669, 194]]
dots_mask = np.zeros((H, W), np.uint8)
for seg in (DOTS[:7], DOTS[7:]):
    pts = np.array(seg, np.int32)
    cv2.polylines(dots_mask, [pts], False, 255, 26)
    for (x, y) in seg:
        cv2.circle(dots_mask, (x, y), 14, 255, -1)

hole = np.zeros((H, W), bool)
for a in given_alpha.values():
    hole |= cv2.dilate((a > 0.02).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) > 0
for m in extra_masks.values():
    hole |= cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))) > 0
hole |= dots_mask > 0
# karakterin zemin gölgesi: kodla karaktere bağlı çizilecek
shadow = np.zeros((H, W), np.uint8)
cv2.ellipse(shadow, (688, 697), (96, 22), 0, 0, 360, 255, -1)
hole |= shadow > 0
# oda çizgileri yeniden çizileceği için orijinal çizgi pikselleri de "bilinmeyen"
lines_mask = np.zeros((H * 4, W * 4), np.uint8)
for p, q, t in LINES:
    cv2.line(lines_mask, (int(p[0] * 4), int(p[1] * 4)), (int(q[0] * 4), int(q[1] * 4)), 255, int(t * 4 + 16), cv2.LINE_AA)
lines_mask = cv2.resize(lines_mask, (W, H), interpolation=cv2.INTER_AREA) > 0

# ---------------------------------------------------------------- düzlem bazlı çok ölçekli doldurma
def fill_plane(img, known, region):
    out = img.copy()
    need = region & ~known
    if not need.any():
        return out
    k = (known & region).astype(np.float32)
    def nc(sig):
        wk = cv2.GaussianBlur(k, (0, 0), sig)
        num = cv2.GaussianBlur(img * k[..., None], (0, 0), sig)
        return num / (wk[..., None] + 1e-6), wk
    f1, w1 = nc(28)
    f2, w2 = nc(90)
    f3, _ = nc(260)
    t2 = np.clip(w2 / 0.08, 0, 1)[..., None]
    base = f2 * t2 + f3 * (1 - t2)
    t1 = np.clip(w1 / 0.12, 0, 1)[..., None]
    fill = f1 * t1 + base * (1 - t1)
    out[need] = fill[need]
    return out


known = ~hole & ~lines_mask
clean = O.copy()
for name, reg in PLANES.items():
    clean = np.where(reg[..., None], fill_plane(O, known, reg), clean)

# dolgu ile orijinal arasında 3 px yumuşak geçiş
fillm = (~known).astype(np.float32)
soft = np.maximum(fillm, cv2.GaussianBlur(fillm, (0, 0), 3))
filled_only = clean.copy()
clean = O * (1 - soft[..., None]) + filled_only * soft[..., None]
clean[~known] = filled_only[~known]
# JPEG dokusunu taklit eden ince gren
rng = np.random.default_rng(3)
noise = rng.normal(0, 1.4, (H, W, 1)).astype(np.float32)
clean = clean + noise * fillm[..., None]

# oda çizgilerini 4x süper örnekleme ile keskin çiz
big = cv2.resize(np.clip(clean, 0, 255).astype(np.uint8), (W * 4, H * 4), interpolation=cv2.INTER_CUBIC)
LINE_COL = (24, 22, 27)
for p, q, t in LINES:
    cv2.line(big, (int(p[0] * 4), int(p[1] * 4)), (int(q[0] * 4), int(q[1] * 4)), LINE_COL, int(round(t * 4)), cv2.LINE_AA)
clean = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
Image.fromarray(clean).save(OUT / "background_clean.png")
print("çizgi rengi", LINE_COL)

# ---------------------------------------------------------------- katman dışa aktarımı
meta = {"canvas": {"width": W, "height": H}, "layers": {}}


def export(name, rgba_canvas):
    a = rgba_canvas[..., 3]
    ys, xs = np.where(a > 0)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    Image.fromarray(rgba_canvas[y0:y1, x0:x1]).save(OUT / f"{name}.png")
    meta["layers"][name] = {"x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0)}


# Orijinalden kesilen eksik öğeler (1 px yumuşak kenar)
for name, m in extra_masks.items():
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
    a = np.clip(a * 1.3, 0, 1)
    rgba = np.dstack([O, a * 255]).astype(np.uint8)
    export(name, rgba)

# Kullanıcı asetleri: balonları iz noktasından ayır
for name, (x, y) in GIVEN.items():
    img = np.asarray(Image.open(SRC / f"{name}.png").convert("RGBA"))
    canvas = np.zeros((H, W, 4), np.uint8)
    canvas[y:y + img.shape[0], x:x + img.shape[1]] = img
    if name.startswith("bubble"):
        n, lab, stats, _ = cv2.connectedComponentsWithStats((canvas[..., 3] > 8).astype(np.uint8))
        order = np.argsort(-stats[1:, cv2.CC_STAT_AREA]) + 1
        main = lab == order[0]
        main = cv2.dilate(main.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        body = canvas.copy(); body[~main] = 0
        dot = canvas.copy(); dot[main] = 0
        export(name, body)
        if dot[..., 3].max() > 0:
            export(name.replace("bubble", "dot"), dot)
    else:
        export(name, canvas)

(OUT / "layers.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
print(json.dumps(meta["layers"], indent=1))

# ---------------------------------------------------------------- doğrulama
comp = Image.fromarray(clean).convert("RGBA")
for name, L in meta["layers"].items():
    comp.alpha_composite(Image.open(OUT / f"{name}.png"), (L["x"], L["y"]))
comp = np.asarray(comp.convert("RGB")).astype(np.float32)
d = np.abs(comp - O).mean(2)
print("yeniden birleşim ort. fark:", round(float(d.mean()), 2), " (nokta çizgisi hariç):",
      round(float(d[dots_mask == 0].mean()), 2))
Image.fromarray(comp.astype(np.uint8)).save(ROOT / "tools" / "check_recomposed.png")
Image.fromarray(np.clip(d * 5, 0, 255).astype(np.uint8)).save(ROOT / "tools" / "check_diff.png")
