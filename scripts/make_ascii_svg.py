#!/usr/bin/env python3
"""
Turn an image (or a word) into a self-typing monochrome ASCII SVG.

  python scripts/make_ascii_svg.py source-prepped.png        # фото -> ASCII
  python scripts/make_ascii_svg.py source.png --invert      # светлый объект на тёмном фоне
  python scripts/make_ascii_svg.py --art data/ascii-art.txt # готовый ASCII из файла
  python scripts/make_ascii_svg.py --text ykosu             # надпись-заглушка

Output: ascii-portrait.svg
"""
import sys, os
from theme import MONO, BG, LINE, PURPLE, CYAN, PINK, COMMENT, esc, window_chrome

RAMP = " .`:-=+*cs#%@"          # bright (sparse) -> dark (dense)
COLS = 92
CHAR_W, CHAR_H = 7.0, 12.4
FONT_SIZE = 11.6
PAD_X, PAD_TOP, PAD_R = 30, 48, 46
ROW_DUR = 0.42                   # seconds per row wipe
ROW_STAGGER = 0.035              # delay between rows


def grid_from_art(path):
    """Готовые ASCII-строки из текстового файла."""
    lines = open(path, encoding="utf-8").read().split("\n")
    lines = [l.rstrip() for l in lines]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def grid_from_image(path, cols=COLS, invert=False):
    from PIL import Image, ImageOps
    im = Image.open(path).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    if invert:                      # светлый объект на тёмном фоне
        im = ImageOps.invert(im)
    w, h = im.size
    # character cells are ~2x taller than wide
    rows = max(1, int(cols * (h / w) * (CHAR_W / CHAR_H)))
    im = im.resize((cols, rows), Image.LANCZOS)
    px = im.load()
    out = []
    n = len(RAMP) - 1
    for y in range(rows):
        line = []
        for x in range(cols):
            v = px[x, y] / 255.0
            line.append(RAMP[int(round((1.0 - v) * n))])
        out.append("".join(line).rstrip())
    # trim fully-blank rows top and bottom
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def grid_from_text(text):
    try:
        import pyfiglet
        art = pyfiglet.figlet_format(text, font="big")
        return [l.rstrip() for l in art.split("\n") if l.strip()]
    except Exception:
        return [f"  {text}  "]


def build_svg(rows, mode="image"):
    global CHAR_W, CHAR_H, FONT_SIZE
    if mode == "text":                    # block-glyph figlet: tighter cells so rows connect
        CHAR_W, CHAR_H, FONT_SIZE = 9.6, 16.0, 16.0
    cols = max((len(r) for r in rows), default=1)
    inner_w = cols * CHAR_W
    w = int(inner_w + PAD_X + PAD_R)
    h = int(PAD_TOP + len(rows) * CHAR_H + 26)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="ASCII portrait">',
        '  <defs>',
        '    <linearGradient id="ink" x1="0" y1="0" x2="0.35" y2="1">',
        f'      <stop offset="0%" stop-color="{PURPLE}"/>',
        f'      <stop offset="55%" stop-color="{PINK}"/>',
        f'      <stop offset="100%" stop-color="{CYAN}"/>',
        '    </linearGradient>',
    ]

    # one clip per row: a rect that wipes left -> right
    for i in range(len(rows)):
        y = PAD_TOP + i * CHAR_H - CHAR_H
        parts.append(f'    <clipPath id="c{i}"><rect x="{PAD_X}" y="{y:.1f}" height="{CHAR_H*1.6:.1f}" width="0">'
                     f'<animate attributeName="width" from="0" to="{inner_w:.1f}" '
                     f'begin="{i*ROW_STAGGER:.2f}s" dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>')
    parts.append('  </defs>')
    parts.append(window_chrome(w, h, "ykosu@github: ~/portrait"))

    parts.append(f'  <g font-family={MONO!r} font-size="{FONT_SIZE}" fill="url(#ink)" '
                 f'xml:space="preserve" style="white-space:pre">')
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        y = PAD_TOP + i * CHAR_H
        parts.append(f'    <text x="{PAD_X}" y="{y:.1f}" textLength="{len(row)*CHAR_W:.1f}" '
                     f'lengthAdjust="spacing" clip-path="url(#c{i})">{esc(row)}</text>')
    parts.append('  </g>')

    # cursor block riding the wipe edge of each row
    parts.append(f'  <g fill="{CYAN}">')
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        y = PAD_TOP + i * CHAR_H - CHAR_H * 0.82
        b = i * ROW_STAGGER
        parts.append(
            f'    <rect x="{PAD_X}" y="{y:.1f}" width="{CHAR_W:.1f}" height="{CHAR_H*0.95:.1f}" opacity="0">'
            f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X+len(row)*CHAR_W:.1f}" '
            f'begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.02;0.9;1" '
            f'begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/></rect>')
    parts.append('  </g>')

    total = len(rows) * ROW_STAGGER + ROW_DUR
    parts.append(f'  <text x="{PAD_X}" y="{h-12}" font-family={MONO!r} font-size="11" fill="{COMMENT}" opacity="0">'
                 f'<animate attributeName="opacity" from="0" to="1" begin="{total:.2f}s" dur="0.6s" fill="freeze"/>'
                 f'ykosu@github ~ $ _</text>')
    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    args = sys.argv[1:]
    invert = "--invert" in args
    args = [a for a in args if a != "--invert"]
    if args and args[0] == "--art":
        rows, mode = grid_from_art(args[1]), "image"
    elif args and args[0] == "--text":
        rows, mode = grid_from_text(args[1] if len(args) > 1 else "ykosu"), "text"
    elif args:
        rows, mode = grid_from_image(args[0], invert=invert), "image"
    else:
        src = "source-prepped.png" if os.path.exists("source-prepped.png") else None
        rows, mode = (grid_from_image(src, invert=invert), "image") if src else (grid_from_text("ykosu"), "text")
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ascii-portrait.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_svg(rows, mode))
    print(f"wrote {out}  ({len(rows)} rows)")
