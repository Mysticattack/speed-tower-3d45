#!/usr/bin/env python3
"""G-code pruefen: Außenwand-Geschwindigkeit je Hoehenband (modales F korrekt mitgefuehrt)."""
import collections
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "speed-tower-3d45.gcode"
BANDS = [(0, 16, 15), (16, 31, 20), (31, 46, 30), (46, 61, 40), (61, 76, 50),
         (76, 91, 60), (91, 106, 70), (106, 121, 80), (121, 136, 90)]

RE_X = re.compile(r"X(-?[0-9.]+)")
RE_Y = re.compile(r"Y(-?[0-9.]+)")
RE_Z = re.compile(r"Z(-?[0-9.]+)")
RE_E = re.compile(r"E(-?[0-9.]+)")
RE_F = re.compile(r"F(-?[0-9.]+)")

xs, ys, zs = [], [], []
z = None
feat = None
f_cur = None
sect = collections.defaultdict(collections.Counter)
by_feat = collections.defaultdict(collections.Counter)

for raw in open(path, errors="ignore"):
    s = raw.strip()
    if s.startswith(";Z:"):
        z = float(s[3:])
        continue
    if s.startswith(";TYPE:"):
        feat = s[6:]
        continue
    if not s.startswith("G1"):
        continue
    body = s[2:]
    # F ist modal: immer mitfuehren, auch auf Nicht-Extrusionszeilen
    mz = RE_Z.search(body)
    if mz:
        z = float(mz.group(1))
    mf = RE_F.search(body)
    if mf:
        f_cur = float(mf.group(1))
    me = RE_E.search(body)
    if not me or float(me.group(1)) <= 0:
        continue
    mx, my = RE_X.search(body), RE_Y.search(body)
    if mx:
        xs.append(float(mx.group(1)))
    if my:
        ys.append(float(my.group(1)))
    zs.append(z)
    speed = round(f_cur / 60) if f_cur else None
    by_feat[feat][speed] += 1
    if feat == "External perimeter":
        band = next((b for lo, hi, b in BANDS if lo <= z < hi), None)
        if band:
            sect[band][speed] += 1

print("Datei:", path)
print("Extrusionen:", len(xs))
print("X: %.2f .. %.2f | Y: %.2f .. %.2f | Z: %.2f .. %.2f"
      % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
print("Bett X -127.5..127.5 / Y -77.5..77.5 -> innerhalb:",
      min(xs) >= -127.5 and max(xs) <= 127.5 and min(ys) >= -77.5 and max(ys) <= 77.5)

print("\nSpeed-Verteilung je Feature (mm/s: Segmente):")
for feat, c in sorted(by_feat.items(), key=lambda kv: -sum(kv[1].values())):
    print(f"  {str(feat):24s} {dict(c.most_common(6))}")

print("\nAußenwand-Speed je Band:")
alles_ok = True
for lo, hi, want in BANDS:
    c = sect.get(want)
    if not c:
        print(f"  Z {lo:3d}-{hi:3d}: Soll {want:2d} -> keine Außenwand-Segmente")
        alles_ok = False
        continue
    total = sum(c.values())
    top, n = c.most_common(1)[0]
    ok = abs(top - want) <= 1 and n / total > 0.95
    alles_ok &= ok
    print(f"  Z {lo:3d}-{hi:3d}: Soll {want:2d} -> Ist {top:3.0f} mm/s "
          f"({n}/{total} = {n/total*100:.1f}%)  {'OK' if ok else 'ABWEICHUNG'}"
          f"   {dict(c.most_common(4))}")
print("\nAlle Baender sauber:", alles_ok)
