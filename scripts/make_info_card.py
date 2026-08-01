#!/usr/bin/env python3
"""Neofetch-style info card -> info-card.svg  (edit ROWS to taste)."""
import json, os
from theme import (MONO, LINE, FG, COMMENT, CYAN, GREEN, ORANGE, PINK,
                   PURPLE, YELLOW, esc, window_chrome)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    _d = json.load(open(os.path.join(ROOT, "data", "stats.json"), encoding="utf-8"))
    REPOS = f'{_d["public_repos"]} public'
    LATEST = _d["repos"][0]["name"] if _d.get("repos") else "-"
except Exception:
    REPOS, LATEST = "6 public", "file-order-manager"

TITLE = "ykosu@github"

# (label, value, value-color)
ROWS = [
    ("OS",        "Windows · WSL2",                          FG),
    ("Shell",     "python3.12 · dotnet",                     FG),
    ("Now",       "Telegram bots & desktop utilities",       CYAN),
    ("Focus",     "Automation, tooling, small useful apps",  FG),
    ("Stack",     "Python · C# · Telegram Bot API",          GREEN),
    ("Libs",      "aiogram · Pillow · WinForms · Tkinter",   FG),
    ("Repos",     REPOS,                                     ORANGE),
    ("Latest",    LATEST,                                    PINK),
    ("Editor",    "VS Code · Git",                           FG),
    ("Motto",     "if it repeats twice, script it",          YELLOW),
]

W = 520
PAD = 26
BAR = 34
LABEL_W = 96
ROW_H = 27
STEP = 0.13


def build():
    top = BAR + 30
    h = int(top + len(ROWS) * ROW_H + 62)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
         f'role="img" aria-label="neofetch info card">',
         '  <defs><style>',
         '    .ln{opacity:0}',
         '    @keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:translateX(0)}}',
         '  </style></defs>',
         window_chrome(W, h, "ykosu@github: ~ $ neofetch")]

    # header
    p.append(f'  <g class="ln" style="animation:in .5s ease-out 0s forwards">')
    p.append(f'    <text x="{PAD}" y="{BAR+26}" font-family={MONO!r} font-size="15" font-weight="bold" '
             f'fill="{PURPLE}">{esc(TITLE)}</text>')
    p.append(f'    <line x1="{PAD}" y1="{BAR+34}" x2="{W-PAD}" y2="{BAR+34}" stroke="{LINE}" stroke-width="1"/>')
    p.append('  </g>')

    for i, (label, value, color) in enumerate(ROWS):
        y = top + 26 + i * ROW_H
        d = (i + 1) * STEP
        p.append(f'  <g class="ln" style="animation:in .45s ease-out {d:.2f}s forwards">')
        p.append(f'    <text x="{PAD}" y="{y}" font-family={MONO!r} font-size="13" font-weight="bold" '
                 f'fill="{CYAN}">{esc(label)}</text>')
        p.append(f'    <text x="{PAD+LABEL_W}" y="{y}" font-family={MONO!r} font-size="13" '
                 f'fill="{color}">{esc(value)}</text>')
        p.append('  </g>')

    # dracula colour swatches, like neofetch's palette row
    sw_y = top + 26 + len(ROWS) * ROW_H + 8
    p.append(f'  <g class="ln" style="animation:in .5s ease-out {(len(ROWS)+1)*STEP:.2f}s forwards">')
    for j, c in enumerate([PURPLE, PINK, CYAN, GREEN, YELLOW, ORANGE, "#ff5555", COMMENT]):
        p.append(f'    <rect x="{PAD + j*26}" y="{sw_y}" width="20" height="12" rx="3" fill="{c}"/>')
    p.append(f'    <text x="{W-PAD}" y="{sw_y+11}" font-family={MONO!r} font-size="11" fill="{COMMENT}" '
             f'text-anchor="end">dracula</text>')
    p.append('  </g>')
    p.append('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "info-card.svg")
    open(out, "w", encoding="utf-8").write(build())
    print("wrote", out)
