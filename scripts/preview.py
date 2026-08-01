#!/usr/bin/env python3
"""Freeze animations and rasterize each SVG to preview/*.png (local check only)."""
import os, re, sys, glob
import cairosvg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "preview")
os.makedirs(OUT, exist_ok=True)


def freeze(svg: str) -> str:
    svg = svg.replace('class="rv"', '').replace('class="ln"', '')
    svg = re.sub(r'style="animation:[^"]*"', '', svg)
    svg = re.sub(r'\.rv\{opacity:0\}', '', svg)
    svg = re.sub(r'\.ln\{opacity:0\}', '', svg)
    svg = svg.replace('opacity="0"', 'opacity="1"')
    # clip rects / bar: give them full width
    svg = re.sub(r'(<rect[^>]*?)width="0"([^>]*?)(?=>)',
                 lambda m: m.group(1) + 'width="100000"' + m.group(2), svg)
    svg = re.sub(r'<animate[^>]*/>', '', svg)
    return svg


for f in sorted(glob.glob(os.path.join(ROOT, "*.svg"))):
    src = open(f, encoding="utf-8").read()
    png = os.path.join(OUT, os.path.basename(f).replace(".svg", ".png"))
    cairosvg.svg2png(bytestring=freeze(src).encode(), write_to=png, scale=1.4)
    print("->", png)
