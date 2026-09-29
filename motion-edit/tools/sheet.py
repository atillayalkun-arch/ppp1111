"""Önizleme karelerinden kontrol tablosu: python3 tools/sheet.py [sütun] [genişlik]"""
import glob
import sys

from PIL import Image, ImageDraw

cols = int(sys.argv[1]) if len(sys.argv) > 1 else 4
w = int(sys.argv[2]) if len(sys.argv) > 2 else 480
h = w * 9 // 16
fs = sorted(glob.glob("preview/*.jpg"))
sheet = Image.new("RGB", (w * cols, h * ((len(fs) + cols - 1) // cols)))
for i, f in enumerate(fs):
    im = Image.open(f).resize((w, h))
    fr = int(f.split("/")[-1][:3])
    ImageDraw.Draw(im).text((6, 6), f"{fr}  ({fr / 30:.2f}s)", fill=(255, 255, 0))
    sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save("tools/sheet.jpg")
