#!/usr/bin/env python3
"""
Перетюнить готовый ASCII без пересборки из фото.

  python scripts/tune_art.py 0.30 1.0    # порог чёрного, гамма
"""
import sys, os

RAMP = " .`:-=+*cs#%@"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "ascii-art-raw.txt")
DST = os.path.join(ROOT, "data", "ascii-art.txt")

thr = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30
gamma = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
n = len(RAMP) - 1
idx = {c: i for i, c in enumerate(RAMP)}

out = []
for line in open(SRC, encoding="utf-8").read().split("\n"):
    s = ""
    for ch in line:
        v = idx.get(ch, 0) / n
        v = max(0.0, (v - thr) / (1.0 - thr)) ** gamma
        s += RAMP[round(v * n)]
    out.append(s.rstrip())
while out and not out[0].strip():
    out.pop(0)
while out and not out[-1].strip():
    out.pop()
open(DST, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"thr={thr} gamma={gamma} -> {DST} ({len(out)} rows)")
