"""Dracula palette + shared SVG helpers."""

BG        = "#282a36"
BG_ALT    = "#21222c"
LINE      = "#44475a"
FG        = "#f8f8f2"
COMMENT   = "#6272a4"
CYAN      = "#8be9fd"
GREEN     = "#50fa7b"
ORANGE    = "#ffb86c"
PINK      = "#ff79c6"
PURPLE    = "#bd93f9"
RED       = "#ff5555"
YELLOW    = "#f1fa8c"

MONO = "'JetBrains Mono','DejaVu Sans Mono','Liberation Mono','Menlo','Consolas','Courier New',monospace"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def window_chrome(w, h, title, r=14):
    """Rounded terminal window: background, title bar, traffic lights, title text."""
    bar = 34
    return f'''  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{r}" fill="{BG}" stroke="{LINE}" stroke-width="1"/>
  <path d="M0.5 {r+0.5} A{r} {r} 0 0 1 {r+0.5} 0.5 L{w-r-0.5} 0.5 A{r} {r} 0 0 1 {w-0.5} {r+0.5} L{w-0.5} {bar} L0.5 {bar} Z" fill="{BG_ALT}"/>
  <line x1="0.5" y1="{bar}" x2="{w-0.5}" y2="{bar}" stroke="{LINE}" stroke-width="1"/>
  <circle cx="20" cy="17" r="6" fill="{RED}"/>
  <circle cx="40" cy="17" r="6" fill="{YELLOW}"/>
  <circle cx="60" cy="17" r="6" fill="{GREEN}"/>
  <text x="{w/2}" y="22" font-family={MONO!r} font-size="12" fill="{COMMENT}" text-anchor="middle">{esc(title)}</text>'''
