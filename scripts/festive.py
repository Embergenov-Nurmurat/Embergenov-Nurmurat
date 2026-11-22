"""New Year decorations: snow, garland, countdown strip.

Everything switches on automatically from Nov 15 to Jan 15 and is removed
afterwards, so nothing has to be cleaned up by hand.
"""
import math
import random
import re
from datetime import date

BULBS = ["#EF4444", "#F59E0B", "#10B981", "#22D3EE", "#A78BFA", "#F472B6"]
CONFETTI = ["#EF4444", "#F59E0B", "#10B981", "#22D3EE", "#A78BFA", "#F472B6", "#FACC15"]
MARK = re.compile(r"<!--ny:start-->.*?<!--ny:end-->", re.S)


def is_festive(today: date) -> bool:
    return (today.month == 11 and today.day >= 15) or today.month == 12 \
        or (today.month == 1 and today.day <= 15)


def css(H):
    return (f"@keyframes ny-fall{{from{{transform:translateY(-24px)}}to{{transform:translateY({H + 24}px)}}}}"
            "@keyframes ny-sway{from{transform:translateX(-9px)}to{transform:translateX(9px)}}"
            "@keyframes ny-blink{0%,100%{opacity:1}50%{opacity:.25}}"
            ".ny-fall{animation:ny-fall linear infinite}"
            ".ny-sway{animation:ny-sway ease-in-out infinite alternate}"
            ".ny-bulb{animation:ny-blink ease-in-out infinite}"
            "@media (prefers-reduced-motion:reduce){.ny-fall,.ny-sway,.ny-bulb{animation:none}}")


def snow(W, H, n=36, seed=1, fill="#FFFFFF", stroke=None, opacity=.85, rmin=1.4, rmax=3.4):
    rnd = random.Random(seed)
    st = f' stroke="{stroke}" stroke-width=".8"' if stroke else ""
    out = []
    for _ in range(n):
        x = rnd.uniform(8, W - 8)
        r = rnd.uniform(rmin, rmax)
        dur = rnd.uniform(9, 18) * (1 + (rmax - r) / 6)   # small flakes drift slower
        delay = -rnd.uniform(0, dur)
        sdur = rnd.uniform(2.5, 5)
        out.append(
            f'<g class="ny-fall" style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s">'
            f'<g class="ny-sway" style="animation-duration:{sdur:.1f}s">'
            f'<circle cx="{x:.1f}" cy="0" r="{r:.1f}" fill="{fill}" fill-opacity="{opacity}"{st}/>'
            f'</g></g>')
    return "".join(out)


def confetti(W, H, n=34, seed=7):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(10, W - 10)
        w, h = rnd.uniform(4, 8), rnd.uniform(7, 13)
        dur = rnd.uniform(5, 10)
        delay = -rnd.uniform(0, dur)
        sdur = rnd.uniform(1.5, 3.5)
        out.append(
            f'<g class="ny-fall" style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s">'
            f'<g class="ny-sway" style="animation-duration:{sdur:.1f}s">'
            f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="{h:.1f}" rx="1.5" '
            f'fill="{CONFETTI[i % len(CONFETTI)]}" fill-opacity=".9" '
            f'transform="rotate({rnd.randint(0, 80)} {x:.1f} 0)"/></g></g>')
    return "".join(out)


def garland(W, y0=6, sag=11, segs=5, margin=40, wire="#64748B", bulb_r=4.2, hang=6):
    """Sagging string of blinking lights. Returns svg fragments."""
    out = []
    seg_w = (W - 2 * margin) / segs
    k = 0
    for s in range(segs):
        x0, x1 = margin + s * seg_w, margin + (s + 1) * seg_w
        cx, cy = (x0 + x1) / 2, y0 + 2 * sag          # control point -> max sag = sag
        out.append(f'<path d="M{x0:.1f} {y0} Q{cx:.1f} {cy} {x1:.1f} {y0}" fill="none" '
                   f'stroke="{wire}" stroke-opacity=".65" stroke-width="1.4"/>')
        for t in (.2, .4, .6, .8):
            bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
            by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y0
            c = BULBS[k % len(BULBS)]
            out.append(
                f'<g class="ny-bulb" style="animation-duration:{1.6 + (k % 4) * .35:.2f}s;'
                f'animation-delay:-{(k * .37) % 2:.2f}s">'
                f'<rect x="{bx-1.6:.1f}" y="{by:.1f}" width="3.2" height="3" fill="{wire}"/>'
                f'<ellipse cx="{bx:.1f}" cy="{by + hang:.1f}" rx="{bulb_r * .78:.1f}" ry="{bulb_r:.1f}" fill="{c}"/>'
                f'<ellipse cx="{bx + .9:.1f}" cy="{by + hang - 1.3:.1f}" rx=".9" ry="1.4" fill="#fff" fill-opacity=".7"/>'
                f'</g>')
            k += 1
    return "".join(out)


def snow_style(theme_name):
    if theme_name == "light":
        return dict(fill="#FFFFFF", stroke="#93C5FD", opacity=.95)
    return dict(fill="#FFFFFF", stroke=None, opacity=.8)


def strip_svg(t, theme_name, today: date):
    """Countdown card (light/dark) in the same terminal style."""
    W, H = 560, 232
    ny = today.year + (0 if today.month == 1 else 1)
    new_year = today.month == 1
    days_left = (date(ny, 1, 1) - today).days
    start = date(today.year, 1, 1)
    total_days = (date(today.year + 1, 1, 1) - start).days
    pct = 100 if new_year else round(((today - start).days + 1) / total_days * 100)
    if new_year:
        big, unit = str(ny), ""
        sub, label = "HAPPY NEW YEAR!", f"{ny}.status: online"
    else:
        big, unit = str(days_left), " day" if days_left == 1 else " days"
        sub, label = f"until {ny}", f"{today.year}.loading... {pct}%"
    bar_w = W - 64
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="New Year countdown">')
    a(f'<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}'
      f'.cur{{animation:b 1.1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}'
      f'.pg{{transform-origin:0 0;transform:scaleX(0);animation:g 1.6s cubic-bezier(.2,.8,.2,1) forwards}}'
      f'@keyframes g{{to{{transform:scaleX(1)}}}}{css(H)}</style>')
    a(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{t["bg1"]}"/><stop offset=".55" stop-color="{t["bg2"]}"/>'
      f'<stop offset="1" stop-color="{t["bg3"]}"/></linearGradient>'
      f'<linearGradient id="bd" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}">'
      f'<stop offset="0" stop-color="{t["b1"]}"/><stop offset=".5" stop-color="{t["b2"]}"/>'
      f'<stop offset="1" stop-color="{t["b3"]}"/></linearGradient>'
      f'<linearGradient id="pgf" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{t["b1"]}"/><stop offset=".5" stop-color="{t["b2"]}"/>'
      f'<stop offset="1" stop-color="{t["b3"]}"/></linearGradient></defs>')
    a(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="28" fill="url(#bg)"/>')
    a(f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="28" fill="none" '
      f'stroke="url(#bd)" stroke-opacity=".6" stroke-width="1.5"/>')
    a(snow(W, H, n=26, seed=11, **snow_style(theme_name)))
    a(garland(W, wire=t["muted"]))
    a(f'<text x="32" y="68" font-size="14" fill="{t["muted"]}">'
      f'$ ./countdown --to {ny}<tspan class="cur" fill="{t["title"]}"> ▌</tspan></text>')
    a(f'<text x="{W/2}" y="130" font-size="54" font-weight="700" text-anchor="middle" fill="{t["text"]}">'
      f'{big}<tspan font-size="22" fill="{t["muted"]}">{unit}</tspan></text>')
    a(f'<text x="{W/2}" y="160" font-size="16" letter-spacing="5" text-anchor="middle" '
      f'fill="{t["title"]}">{sub}</text>')
    a(f'<rect x="32" y="182" width="{bar_w}" height="8" rx="4" fill="{t["track"]}" fill-opacity=".6"/>')
    a(f'<rect class="pg" x="32" y="182" width="{max(bar_w * pct / 100, 8):.1f}" height="8" rx="4" fill="url(#pgf)"/>')
    a(f'<text x="32" y="214" font-size="13" fill="{t["muted"]}">{label}</text>')
    if new_year:
        a(confetti(W, H))
    a('</svg>')
    return "".join(o)


def empty_svg():
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1" viewBox="0 0 1 1"/>'


def apply_to_banner(path, theme_name, t, active):
    """Idempotently adds (or removes) snow + garland to an existing banner svg."""
    s = open(path, encoding="utf-8").read()
    s = MARK.sub("", s)
    if active:
        m = re.search(r'<svg[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"', s)
        W, H = int(m.group(1)), int(m.group(2))
        block = (f'<!--ny:start--><g pointer-events="none"><style>{css(H)}</style>'
                 f'{snow(W, H, n=40, seed=3, **snow_style(theme_name))}'
                 f'{garland(W, y0=5, sag=9, segs=8, margin=60, wire=t["muted"], bulb_r=3.6, hang=5)}'
                 f'</g><!--ny:end-->')
        i = s.rfind("</svg>")
        s = s[:i] + block + "\n" + s[i:]
    open(path, "w", encoding="utf-8").write(s)
