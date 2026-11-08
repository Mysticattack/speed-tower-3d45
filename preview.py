#!/usr/bin/env python3
"""Vorschaubild aus dem G-code: Vorderansicht (X/Z) mit farbigen Baendern + Draufsicht."""
import re
from PIL import Image, ImageDraw, ImageFont

PATH = "speed-tower-3d45.gcode"
OUT = "speed-tower-3d45-vorschau.png"

BANDS = [(0, 16, 15), (16, 31, 20), (31, 46, 30), (46, 61, 40), (61, 76, 50),
         (76, 91, 60), (91, 106, 70), (106, 121, 80), (121, 136, 90)]
COLORS = ["#2b6cb0", "#2f855a", "#68a063", "#b7a633", "#d69e2e", "#dd6b20",
          "#c53030", "#9b2c2c", "#6b46c1"]

RE_X = re.compile(r"X(-?[0-9.]+)")
RE_Y = re.compile(r"Y(-?[0-9.]+)")
RE_Z = re.compile(r"Z(-?[0-9.]+)")
RE_E = re.compile(r"E(-?[0-9.]+)")

pts = []
z = None
for raw in open(PATH, errors="ignore"):
    s = raw.strip()
    if s.startswith(";Z:"):
        z = float(s[3:])
        continue
    if not s.startswith("G1"):
        continue
    b = s[2:]
    mz = RE_Z.search(b)
    if mz:
        z = float(mz.group(1))
    me = RE_E.search(b)
    if not me or float(me.group(1)) <= 0:
        continue
    mx, my = RE_X.search(b), RE_Y.search(b)
    if mx and my:
        pts.append((float(mx.group(1)), float(my.group(1)), z))

print("Punkte:", len(pts))

# --- Vorderansicht X/Z ---
S = 7.0
W, H = 420, 1060
img = Image.new("RGB", (W + 260, H + 90), "#0f1117")
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
except OSError:
    font = font_s = font_b = ImageFont.load_default()

ox, oy = 40, H + 30          # Ursprung unten links
def px(x, z):
    return (ox + (x + 25) * S, oy - z * S)

# Bettlinie + Bandgrenzen
d.line([(ox - 15, oy), (ox + 60 * S, oy)], fill="#555", width=2)
for i, (lo, hi, speed) in enumerate(BANDS):
    y0 = px(0, hi)[1]
    y1 = px(0, lo)[1]
    if i % 2 == 0:
        d.rectangle([ox - 15, y0, ox + 60 * S, y1], fill="#171a22")
    d.line([(ox - 15, y0), (ox + 25, y0)], fill="#333", width=1)
    d.text((ox + 27, (y0 + y1) / 2 - 9), f"{speed} mm/s", font=font, fill=COLORS[i])

for x, y, z in pts:
    c = "#888"
    for i, (lo, hi, speed) in enumerate(BANDS):
        if lo <= z < hi:
            c = COLORS[i]
            break
    X, Y = px(x, z)
    d.point((X, Y), fill=c)

d.text((40, 14), "Speed-Tower auf Dremel 3D45", font=font_b, fill="#e8e8e8")
d.text((40, 40), "Vorderansicht X/Z, 20 mm Wuerfel, Hoehe 135,8 mm, 0,15 mm Layer",
       font=font_s, fill="#9aa0aa")

# --- Draufsicht X/Y ---
TX, TY = W + 35, 120
d.text((TX, TY - 30), "Draufsicht", font=font, fill="#e8e8e8")
S2 = 1.9
cx, cy = TX + 130, TY + 135
d.rectangle([cx - 20 * S2, cy - 20 * S2, cx + 20 * S2, cy + 20 * S2], outline="#333")
for i, (lo, hi, speed) in enumerate(BANDS):
    for x, y, z in pts[::7]:
        if lo <= z < hi:
            d.point((cx + x * S2, cy - y * S2), fill=COLORS[i])

d.text((TX, TY + 320), "Bett", font=font_s, fill="#9aa0aa")
d.text((TX, TY + 340), "255 x 155 mm, Mitte 0/0", font=font_s, fill="#9aa0aa")
d.text((TX, TY + 375), "Duese 215 °C / Bett 60 °C", font=font_s, fill="#9aa0aa")
d.text((TX, TY + 395), "Aussenwand je 15 mm:", font=font_s, fill="#9aa0aa")
for i, (lo, hi, speed) in enumerate(BANDS):
    d.text((TX, TY + 418 + i * 18), f"Z {lo:3d}-{hi:3d} mm   {speed:2d} mm/s",
           font=font_s, fill=COLORS[i])

img.save(OUT)
print("geschrieben:", OUT, img.size)
