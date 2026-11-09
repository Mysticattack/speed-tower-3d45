#!/usr/bin/env python3
"""G-code fuer den Dremel 3D45 nachbearbeiten.

Zwei Dinge, die PrusaSlicer anders macht als der Dremel-Slicer:
1. Zahlen ohne fuehrende Null ("Z.2", "E.76013") -> die Dremel-Firmware parst eigen,
   solche Tokens sind riskant. Alles wird auf 0.xxx normiert.
2. Z-Verfahrten mit Reise-F-Geschwindigkeit (F7800 = 130 mm/s) -> die Z-Achse des
   3D45 kann laut Profil 12 mm/s. Alle Bewegungen mit Z-Anteil werden auf F720 gekappt.
"""
import re
import sys

IN = sys.argv[1]
OUT = sys.argv[2]
MAX_Z_F = 720          # 12 mm/s
MAX_F = 7800           # 130 mm/s Reise

TOK = re.compile(r"([XYZEFIJKR])(-?\d*\.?\d+)")


def fix_num(val, decimals):
    return f"{float(val):.{decimals}f}"


def main():
    out_lines = []
    changed_num = 0
    changed_f = 0
    for raw in open(IN, errors="ignore"):
        line = raw.rstrip("\n")
        s = line.strip()
        if not s or s.startswith(";") or s.startswith("("):
            out_lines.append(line)
            continue
        cmd = s.split()[0] if s.split() else ""
        if cmd not in ("G0", "G1", "G2", "G3"):
            out_lines.append(line)
            continue

        comment = ""
        if ";" in line:
            body, comment = line.split(";", 1)
            comment = ";" + comment
        else:
            body = line

        tokens = TOK.findall(body)
        if not tokens:
            out_lines.append(line)
            continue

        has_z = any(t[0] == "Z" for t in tokens)
        # F-Wert bestimmen
        f_val = None
        for axis, val in tokens:
            if axis == "F":
                f_val = float(val)

        if f_val is not None:
            limit = MAX_Z_F if has_z else MAX_F
            if f_val > limit:
                f_val = limit
                changed_f += 1

        parts = [cmd.rstrip(".")]
        for axis, val in tokens:
            if axis == "F":
                continue
            if axis == "E":
                new = fix_num(val, 5)
            else:
                new = fix_num(val, 3)
            if new != val and not (axis in "XYZ" and new == fix_num(val, 3)):
                changed_num += 1
            parts.append(axis + new)
        if f_val is not None:
            parts.append("F" + fix_num(f_val, 3))

        new_line = " ".join(parts)
        if comment:
            new_line += " " + comment.strip()
        out_lines.append(new_line)

    out_lines.insert(0, "; nachbearbeitet fuer Dremel 3D45: Zahlen mit fuehrender Null, Z-F max 720")
    with open(OUT, "w") as f:
        f.write("\n".join(out_lines) + "\n")
    print(f"geschrieben: {OUT}")
    print(f"Zahlen normalisiert: {changed_num} Tokens, F-Korrekturen: {changed_f}")


if __name__ == "__main__":
    main()
