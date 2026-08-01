#!/usr/bin/env python3
"""data/stats.json -> stats-panel.svg (animated, reveals once then freezes)."""
import json, os
from theme import (MONO, BG_ALT, LINE, FG, COMMENT, CYAN, GREEN, ORANGE,
                   PINK, PURPLE, YELLOW, RED, esc, window_chrome)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, PAD, BAR = 880, 26, 34

LANG_COLORS = {
    "Python": "#3572A5", "C#": "#178600", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "HTML": "#e34c26", "CSS": "#563d7c", "Go": "#00ADD8", "Rust": "#dea584",
    "Java": "#b07219", "C++": "#f34b7d", "Shell": "#89e051",
}
ACCENTS = [PURPLE, PINK, CYAN, GREEN, YELLOW, ORANGE]


def counter(x, y, w, value, label, color, delay):
    return f'''  <g class="rv" style="animation:pop .5s cubic-bezier(.2,.8,.3,1.2) {delay:.2f}s forwards">
    <rect x="{x}" y="{y}" width="{w}" height="88" rx="10" fill="{BG_ALT}" stroke="{LINE}"/>
    <rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="{color}"/>
    <text x="{x+w/2}" y="{y+50}" font-family={MONO!r} font-size="32" font-weight="bold" fill="{color}" text-anchor="middle">{esc(str(value))}</text>
    <text x="{x+w/2}" y="{y+72}" font-family={MONO!r} font-size="11" fill="{COMMENT}" text-anchor="middle">{esc(label)}</text>
  </g>'''


def build(d):
    langs = d["languages"] or {"—": 1}
    tot = sum(langs.values())
    repos = d["repos"]
    c = d["contributions"]

    h = BAR + 30 + 88 + 34 + 58 + 26 + len(repos) * 26 + 46
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
         f'role="img" aria-label="GitHub stats panel">',
         '  <defs><style>',
         '    .rv{opacity:0}',
         '    @keyframes pop{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}',
         '    @keyframes slide{from{opacity:0;transform:translateX(-16px)}to{opacity:1;transform:translateX(0)}}',
         '  </style></defs>',
         window_chrome(W, h, "ykosu@github: ~ $ ./stats.sh")]

    # ── counters ────────────────────────────────────────────────────────────
    y = BAR + 24
    items = [
        (d["public_repos"],        "PUBLIC REPOS",        PURPLE),
        (len(langs),               "LANGUAGES",           CYAN),
        (c["total_year"],          "CONTRIBUTIONS / 12M", GREEN),
        (c["active_days"],         "ACTIVE DAYS",         YELLOW),
        (d["stars_received"],      "STARS EARNED",        ORANGE),
        (c["longest_streak"],      "LONGEST STREAK",      PINK),
    ]
    gap, n = 14, len(items)
    cw = (W - PAD * 2 - gap * (n - 1)) / n
    for i, (v, lb, col) in enumerate(items):
        p.append(counter(PAD + i * (cw + gap), y, cw, v, lb, col, 0.10 + i * 0.09))

    # ── language bar ────────────────────────────────────────────────────────
    y2 = y + 88 + 34
    p.append(f'  <text x="{PAD}" y="{y2-12}" font-family={MONO!r} font-size="12" fill="{COMMENT}">'
             f'language mix</text>')
    bw = W - PAD * 2
    x = PAD
    p.append(f'  <clipPath id="barclip"><rect x="{PAD}" y="{y2}" width="0" height="16" rx="8">'
             f'<animate attributeName="width" from="0" to="{bw}" begin="0.75s" dur="0.9s" '
             f'calcMode="spline" keySplines="0.2 0.8 0.3 1" fill="freeze"/></rect></clipPath>')
    p.append(f'  <g clip-path="url(#barclip)">')
    for i, (lang, cnt) in enumerate(langs.items()):
        seg = bw * cnt / tot
        col = LANG_COLORS.get(lang, ACCENTS[i % len(ACCENTS)])
        p.append(f'    <rect x="{x:.1f}" y="{y2}" width="{seg:.1f}" height="16" fill="{col}"/>')
        x += seg
    p.append('  </g>')

    lx = PAD
    for i, (lang, cnt) in enumerate(langs.items()):
        col = LANG_COLORS.get(lang, ACCENTS[i % len(ACCENTS)])
        pct = 100.0 * cnt / tot
        label = f"{lang} {pct:.1f}%"
        p.append(f'  <g class="rv" style="animation:pop .4s ease-out {1.15+i*0.1:.2f}s forwards">'
                 f'<circle cx="{lx+5}" cy="{y2+36}" r="5" fill="{col}"/>'
                 f'<text x="{lx+16}" y="{y2+40}" font-family={MONO!r} font-size="12" fill="{FG}">{esc(label)}</text></g>')
        lx += 22 + len(label) * 7.2

    # ── repo list ───────────────────────────────────────────────────────────
    y3 = y2 + 58 + 26
    p.append(f'  <text x="{PAD}" y="{y3-14}" font-family={MONO!r} font-size="12" fill="{COMMENT}">'
             f'recent repositories</text>')
    for i, r in enumerate(repos):
        ry = y3 + 6 + i * 26
        col = LANG_COLORS.get(r["language"], ACCENTS[i % len(ACCENTS)])
        p.append(f'  <g class="rv" style="animation:slide .45s ease-out {1.5+i*0.11:.2f}s forwards">'
                 f'<text x="{PAD}" y="{ry}" font-family={MONO!r} font-size="13" fill="{GREEN}">$</text>'
                 f'<text x="{PAD+18}" y="{ry}" font-family={MONO!r} font-size="13" fill="{FG}">{esc(r["name"])}</text>'
                 f'<circle cx="{PAD+330}" cy="{ry-4}" r="5" fill="{col}"/>'
                 f'<text x="{PAD+344}" y="{ry}" font-family={MONO!r} font-size="12" fill="{COMMENT}">{esc(r["language"])}</text>'
                 f'<text x="{PAD+470}" y="{ry}" font-family={MONO!r} font-size="12" fill="{YELLOW}">★ {r["stars"]}</text>'
                 f'<text x="{W-PAD}" y="{ry}" font-family={MONO!r} font-size="12" fill="{COMMENT}" '
                 f'text-anchor="end">{esc(r["updated"])}</text></g>')

    p.append(f'  <text x="{W/2}" y="{h-14}" font-family={MONO!r} font-size="11" fill="{COMMENT}" '
             f'text-anchor="middle" class="rv" style="animation:pop .5s ease-out 2.3s forwards">'
             f'auto-generated · {esc(d["generated"])}</text>')
    p.append('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    d = json.load(open(os.path.join(ROOT, "data", "stats.json"), encoding="utf-8"))
    out = os.path.join(ROOT, "stats-panel.svg")
    open(out, "w", encoding="utf-8").write(build(d))
    print("wrote", out)
