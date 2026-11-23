#!/usr/bin/env python3
"""Front-page newspaper for Sunday 22 November 2026 (1024x1024 PNG).

Layout follows the winning front-page pattern: masthead, headline
numbers, region tabs, 3 lead cards, 10 illustrated cards, a numbered
world map, an ALSO ON SUNDAY list, a UTC timeline and a red DATE CHECK
box. Status pills mark every illustrated story: REPORTED / CLAIM /
CONFIRMED / ONGOING — an unconfirmed claim is never stated as fact.

Deterministic: fixed fonts, fixed palette, no network, no randomness.
Reads stories.json from dev/real and writes entry.png beside it.
Run twice -> byte-identical output.
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "..", "dev", "real", "stories.json")))

W = H = 1024
PAPER = (247, 242, 231)
INK = (25, 25, 25)
NAVY = (20, 38, 74)
NAVY2 = (28, 52, 96)
AMBER = (232, 163, 23)
RED = (179, 64, 46)
TEAL = (31, 111, 107)
GREEN = (46, 125, 70)
CARD = (255, 255, 255)
LINE = (200, 192, 172)
MUTED = (90, 86, 76)
SKY = (168, 205, 226)
SEA = (44, 92, 140)
OCEAN = (178, 208, 228)
LAND = (232, 222, 196)

PILL_FILL = {"REPORTED": NAVY, "CLAIM": AMBER, "CONFIRMED": GREEN,
             "ONGOING": RED}
PILL_TEXT = {"REPORTED": (255, 255, 255), "CLAIM": (25, 25, 25),
             "CONFIRMED": (255, 255, 255), "ONGOING": (255, 255, 255)}


def font(name, size):
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/" + name + ".ttf", size)


SERIF_B = lambda s: font("DejaVuSerif-Bold", s)
SANS_B = lambda s: font("DejaVuSans-Bold", s)
SANS = lambda s: font("DejaVuSans", s)


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, width, max_lines, bold=True, shrink_to=10):
    size = fnt.size
    while size > shrink_to:
        name = "DejaVuSans-Bold" if bold else "DejaVuSans"
        f = font(name, size)
        lines = wrap(draw, text, f, width)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = font("DejaVuSans-Bold" if bold else "DejaVuSans", shrink_to)
    lines = wrap(draw, text, f, width)
    if len(lines) > max_lines:
        # Never silently truncate mid-sentence: fail loudly so a cut-off
        # dek is caught at build time, not by a human reading a crop.
        raise ValueError(
            "text needs %d lines, max %d at min size %d: %r -> %r"
            % (len(lines), max_lines, shrink_to, text, lines))
    return f, lines


def pill(draw, x, y, text, size=10):
    f = SANS_B(size)
    w = draw.textlength(text, font=f) + 10
    draw.rounded_rectangle([x, y, x + w, y + size + 8], radius=3,
                           fill=PILL_FILL[text])
    draw.text((x + 5, y + 4), text, font=f, fill=PILL_TEXT[text])
    return w


def num_badge(draw, x, y, n, r=10):
    draw.ellipse([x, y, x + 2 * r, y + 2 * r], fill=RED)
    draw.ellipse([x, y, x + 2 * r, y + 2 * r], outline=(255, 255, 255), width=1)
    t = str(n)
    f = SANS_B(12 if n < 10 else 10)
    tw = draw.textlength(t, font=f)
    draw.text((x + r - tw / 2, y + r - 7), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- icons
def icon_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h - 26, x + w, y + h], fill=SEA)
    for i in range(4):
        d.arc([x + 8 + i * 26, y + h - 34, x + 30 + i * 26, y + h - 12],
              200, 340, fill=(255, 255, 255), width=3)
    d.polygon([(x + 18, y + 52), (x + w - 18, y + 52), (x + w - 34, y + 74),
               (x + 34, y + 74)], fill=(60, 60, 66))
    d.rectangle([x + 30, y + 30, x + 52, y + 52], fill=RED)
    d.rectangle([x + 56, y + 30, x + 78, y + 52], fill=AMBER)
    d.rectangle([x + 82, y + 30, x + 104, y + 52], fill=TEAL)
    d.rectangle([x + w - 46, y + 34, x + w - 26, y + 52], fill=(240, 240, 240))
    cx, cy = x + w - 36, y + 16
    d.polygon([(cx, cy - 12), (cx + 9, cy + 4), (cx + 4, cy + 2),
               (cx + 6, cy + 10), (cx, cy + 4), (cx - 6, cy + 10),
               (cx - 4, cy + 2), (cx - 9, cy + 4)], fill=(255, 140, 0))


def icon_capitol(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 240))
    cx = x + w // 2
    d.pieslice([cx - 34, y + 8, cx + 34, y + 62], 180, 360, fill=(255, 255, 255))
    d.rectangle([cx - 40, y + 52, cx + 40, y + 60], fill=(255, 255, 255))
    for i in range(-2, 3):
        d.rectangle([cx + i * 16 - 4, y + 60, cx + i * 16 + 4, y + 84],
                    fill=(255, 255, 255))
    d.rectangle([x + 8, y + 84, x + w - 8, y + 92], fill=(255, 255, 255))
    d.line([cx, y + 2, cx, y + 10], fill=RED, width=3)
    d.polygon([(cx, y + 2), (cx + 12, y + 6), (cx, y + 10)], fill=RED)


def icon_globe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 60, 80))
    cx, cy, r = x + w // 2, y + h // 2 + 4, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 140, 90))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 60, 300, fill=(255, 255, 255), width=2)
    d.line([cx, cy - r, cx, cy + r], fill=(255, 255, 255), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=(255, 255, 255), width=2)
    d.ellipse([x + w - 26, y + 10, x + w - 8, y + 28], fill=AMBER)
    for a in range(8):
        ang = a * math.pi / 4
        d.line([x + w - 17 + 12 * math.cos(ang), y + 19 + 12 * math.sin(ang),
                x + w - 17 + 17 * math.cos(ang), y + 19 + 17 * math.sin(ang)],
               fill=AMBER, width=2)


def icon_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 196))
    d.rectangle([x, y + h - 24, x + w, y + h], fill=SEA)
    d.polygon([(x + 16, y + 56), (x + w - 16, y + 56), (x + w - 30, y + 76),
               (x + 30, y + 76)], fill=(90, 90, 96))
    d.rectangle([x + w // 2 - 4, y + 24, x + w // 2 + 4, y + 56], fill=(60, 60, 66))
    d.rectangle([x + w // 2 + 4, y + 26, x + w // 2 + 26, y + 44], fill=RED)
    cx, cy = x + 30, y + 22
    for dx, dy in [(0, -12), (10, -7), (12, 4), (6, 12), (-6, 12), (-12, 4),
                   (-10, -7)]:
        d.line([cx, cy, cx + dx, cy + dy], fill=(255, 140, 0), width=3)


def icon_shield(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 240))
    cx = x + w // 2
    d.polygon([(cx - 30, y + 14), (cx + 30, y + 14), (cx + 30, y + 48),
               (cx, y + 82), (cx - 30, y + 48)], fill=NAVY)
    d.polygon([(cx - 22, y + 21), (cx + 22, y + 21), (cx + 22, y + 46),
               (cx, y + 72), (cx - 22, y + 46)], fill=(255, 255, 255))
    d.text((cx - 7, y + 30), "\u2605", font=SANS_B(22), fill=AMBER)


def icon_tennis(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 111, 107))
    cx, cy, r = x + w // 2, y + h // 2, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(190, 220, 60))
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=(255, 255, 255), width=3)
    d.arc([cx - r, cy - r, cx + r, cy + r], 120, 240, fill=(255, 255, 255), width=3)


def icon_football(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 111, 107))
    cx, cy, r = x + w // 2, y + h // 2, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    pts = []
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        pts.append((cx + 12 * math.cos(a), cy + 12 * math.sin(a)))
    d.polygon(pts, fill=INK)
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        d.line([cx + 12 * math.cos(a), cy + 12 * math.sin(a),
                cx + 27 * math.cos(a), cy + 27 * math.sin(a)], fill=INK, width=2)


def icon_badge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 224, 190))
    cx, cy = x + w // 2, y + h // 2 - 6
    outer = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = 32 if i % 2 == 0 else 16
        outer.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(outer, fill=AMBER)
    d.polygon([(cx - 12, cy + 30), (cx + 12, cy + 30), (cx + 8, cy + 44),
               (cx - 8, cy + 44)], fill=RED)


def icon_golf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 180, 90))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(70, 130, 60))
    cx = x + w // 2
    d.line([cx, y + 18, cx, y + 76], fill=(255, 255, 255), width=3)
    d.polygon([(cx, y + 18), (cx + 30, y + 28), (cx, y + 38)], fill=RED)
    d.ellipse([cx + 18, y + 70, cx + 30, y + 82], fill=(255, 255, 255))


def icon_target(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 196))
    cx, cy = x + w // 2, y + h // 2
    for r, col in [(34, RED), (24, (255, 255, 255)), (14, RED)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)


def icon_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 240))
    cx, cy = x + w // 2, y + h // 2
    d.rounded_rectangle([cx - 30, cy - 26, cx + 30, cy + 30], radius=4,
                        fill=(255, 255, 255), outline=NAVY, width=2)
    d.line([cx - 22, cy + 2, cx - 8, cy + 16], fill=GREEN, width=5)
    d.line([cx - 8, cy + 16, cx + 24, cy - 18], fill=GREEN, width=5)
    d.rectangle([cx - 30, cy + 34, cx + 30, cy + 38], fill=NAVY)


def icon_flag(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 111, 107))
    cx = x + w // 2
    d.line([cx - 26, y + 16, cx - 26, y + 82], fill=(255, 255, 255), width=3)
    for r in range(3):
        for c in range(4):
            if (r + c) % 2 == 0:
                d.rectangle([cx - 24 + c * 12, y + 16 + r * 12,
                             cx - 12 + c * 12, y + 28 + r * 12],
                            fill=INK)
            else:
                d.rectangle([cx - 24 + c * 12, y + 16 + r * 12,
                             cx - 12 + c * 12, y + 28 + r * 12],
                            fill=(255, 255, 255))


def icon_basketball(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 111, 107))
    cx, cy, r = x + w // 2, y + h // 2, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(235, 120, 40))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    d.line([cx, cy - r, cx, cy + r], fill=INK, width=2)
    d.line([cx - r, cy, cx + r, cy], fill=INK, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=INK, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 120, 240, fill=INK, width=2)


ICONS = {"tanker": icon_tanker, "capitol": icon_capitol, "globe": icon_globe,
         "ship": icon_ship, "shield": icon_shield, "tennis": icon_tennis,
         "football": icon_football, "badge": icon_badge, "golf": icon_golf,
         "target": icon_target, "ballot": icon_ballot, "flag": icon_flag,
         "basketball": icon_basketball}

# Rough continent outlines, normalised (0..1) inside the map panel.
CONTINENTS = [
    [(0.05, 0.25), (0.10, 0.10), (0.20, 0.08), (0.28, 0.18), (0.30, 0.35),
     (0.24, 0.45), (0.18, 0.55), (0.12, 0.50), (0.06, 0.40)],
    [(0.30, 0.05), (0.34, 0.05), (0.34, 0.14), (0.30, 0.14)],
    [(0.26, 0.55), (0.32, 0.52), (0.36, 0.60), (0.34, 0.75), (0.30, 0.90),
     (0.27, 0.75)],
    [(0.46, 0.12), (0.52, 0.08), (0.56, 0.14), (0.55, 0.24), (0.50, 0.28),
     (0.46, 0.22)],
    [(0.47, 0.32), (0.55, 0.30), (0.60, 0.38), (0.58, 0.55), (0.53, 0.68),
     (0.49, 0.55), (0.46, 0.42)],
    [(0.56, 0.08), (0.70, 0.05), (0.85, 0.10), (0.95, 0.20), (0.92, 0.35),
     (0.85, 0.45), (0.75, 0.50), (0.65, 0.45), (0.58, 0.35), (0.56, 0.20)],
    [(0.82, 0.68), (0.90, 0.66), (0.93, 0.74), (0.88, 0.82), (0.83, 0.76)],
]


# ---------------------------------------------------------------- page
def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 14

    # ---- masthead
    d.rectangle([0, 0, W, 84], fill=NAVY)
    d.rectangle([0, 84, W, 88], fill=AMBER)
    d.text((M, 10), "THE WORLD IN ONE PAGE", font=SERIF_B(32),
           fill=(255, 255, 255))
    d.text((M, 52), "SUNDAY 22 NOVEMBER 2026  \u00b7  THE DAY'S NEWS, IN ONE IMAGE",
           font=SANS_B(14), fill=AMBER)
    d.text((W - M - 200, 14), "33 STORIES", font=SANS_B(25),
           fill=(255, 255, 255))
    d.text((W - M - 200, 50), "7 REGIONS", font=SANS_B(13),
           fill=(200, 210, 230))

    # ---- numbers strip
    ny = 88
    d.rectangle([0, ny, W, ny + 40], fill=NAVY2)
    nums = DATA["numbers"]
    seg = W // len(nums)
    for i, n in enumerate(nums):
        cx = i * seg + seg // 2
        d.text((cx, ny + 3), n["value"], font=SANS_B(16), fill=AMBER,
               anchor="ma")
        lab = wrap(d, n["label"].upper(), SANS_B(7), seg - 8)
        ly = ny + 23
        for ln in lab[:2]:
            d.text((cx, ly), ln, font=SANS_B(7), fill=(200, 210, 230),
                   anchor="ma")
            ly += 9

    # ---- region tabs
    ty = 128
    d.rectangle([0, ty, W, ty + 24], fill=(255, 255, 255))
    d.rectangle([0, ty + 24, W, ty + 25], fill=LINE)
    regs = DATA["regions"]
    tw = (W - 2 * M) // len(regs)
    for i, r in enumerate(regs):
        x = M + i * tw
        d.text((x + 4, ty + 5), r["name"], font=SANS_B(11), fill=NAVY)
        d.text((x + tw - 26, ty + 5), str(r["count"]), font=SANS_B(12),
               fill=RED)
        if i:
            d.line([x, ty + 4, x, ty + 20], fill=LINE, width=1)

    # ---- leads: 3 big cards
    y0, lh = 160, 158
    cw = (W - 2 * M - 20) // 3
    for i, st in enumerate(DATA["leads"]):
        x = M + i * (cw + 10)
        d.rounded_rectangle([x, y0, x + cw, y0 + lh], radius=6, fill=CARD,
                            outline=LINE, width=1)
        ICONS[st["icon"]](d, x + 6, y0 + 6, cw - 12, 70)
        num_badge(d, x + 10, y0 + 10, i + 1)
        pw = pill(d, x + 10, y0 + 82, st["pill"], size=9)
        d.text((x + 14 + pw, y0 + 85), st["region"], font=SANS_B(9), fill=RED)
        f, lines = fit_lines(d, st["headline"], SANS_B(16), cw - 20, 2)
        yy = y0 + 102
        for ln in lines:
            d.text((x + 10, yy), ln, font=f, fill=INK)
            yy += f.size + 2
        sf, slines = fit_lines(d, st["sub"], SANS(11), cw - 20, 2, bold=False)
        for ln in slines:
            d.text((x + 10, yy), ln, font=sf, fill=MUTED)
            yy += sf.size + 1

    # ---- illustrated: 10 cards, 5 x 2
    y1, ih = 326, 106
    tw5 = (W - 2 * M - 24) // 5
    for i, st in enumerate(DATA["illustrated"]):
        r, c = divmod(i, 5)
        x = M + c * (tw5 + 6)
        y = y1 + r * (ih + 8)
        d.rounded_rectangle([x, y, x + tw5, y + ih], radius=6, fill=CARD,
                            outline=LINE, width=1)
        ICONS[st["icon"]](d, x + 5, y + 5, 62, ih - 10)
        num_badge(d, x + 8, y + 8, i + 4, r=9)
        tx = x + 72
        pw = pill(d, tx, y + 6, st["pill"], size=8)
        d.text((tx + pw + 4, y + 8), st["region"], font=SANS_B(8), fill=RED)
        f, lines = fit_lines(d, st["headline"], SANS_B(12), tw5 - 78, 3)
        yy = y + 24
        for ln in lines:
            d.text((tx, yy), ln, font=f, fill=INK)
            yy += f.size + 1
        sf, slines = fit_lines(d, st["sub"], SANS(10), tw5 - 78, 2, bold=False)
        for ln in slines:
            d.text((tx, yy), ln, font=sf, fill=MUTED)
            yy += sf.size + 1

    # ---- world map with numbered pins
    my = 550
    d.text((M, my), "WHERE IT HAPPENED", font=SANS_B(13), fill=NAVY)
    d.text((W - M, my), "pins 1\u201313 match the cards above",
           font=SANS(11), fill=MUTED, anchor="ra")
    mx, mw, mh = M, W - 2 * M, 132
    my0 = my + 20
    d.rectangle([mx, my0, mx + mw, my0 + mh], fill=OCEAN, outline=LINE)
    for poly in CONTINENTS:
        pts = [(mx + px * mw, my0 + py * mh) for px, py in poly]
        d.polygon(pts, fill=LAND, outline=(180, 170, 140))
    # Urals line, so Europe reads apart from Asia
    d.line([(mx + 0.565 * mw, my0 + 0.06 * mh),
            (mx + 0.585 * mw, my0 + 0.34 * mh)],
           fill=(150, 138, 105), width=2)
    all_cards = DATA["leads"] + DATA["illustrated"]
    for i, st in enumerate(all_cards):
        px, py = st["pin"]
        cx, cy = mx + px * mw, my0 + py * mh
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=RED,
                  outline=(255, 255, 255), width=2)
        t = str(i + 1)
        f = SANS_B(11 if i + 1 < 10 else 9)
        tw = d.textlength(t, font=f)
        d.text((cx - tw / 2, cy - 7), t, font=f, fill=(255, 255, 255))

    # ---- ALSO ON SUNDAY list
    ay = 712
    d.text((M, ay), "ALSO ON SUNDAY", font=SANS_B(13), fill=NAVY)
    d.text((W - M, ay), "14\u201333  \u00b7  status in grey",
           font=SANS(11), fill=MUTED, anchor="ra")
    col_w = (W - 2 * M - 20) // 2
    for i, st in enumerate(DATA["also"]):
        c, r = divmod(i, 10)
        x = M + c * (col_w + 20)
        y = ay + 22 + r * 15
        d.text((x, y), str(14 + i) + ".", font=SANS_B(11), fill=RED)
        d.text((x + 26, y), st["headline"], font=SANS(11), fill=INK)
        hw = d.textlength(st["headline"], font=SANS(11))
        d.text((x + 26 + hw + 6, y), st["pill"], font=SANS_B(8), fill=MUTED)

    # ---- UTC timeline
    ty2 = 890
    d.rectangle([0, ty2, W, ty2 + 34], fill=NAVY)
    d.text((M, ty2 + 3), "SUNDAY IN UTC", font=SANS_B(11), fill=AMBER)
    tl = DATA["timeline"]
    seg2 = (W - 2 * M - 130) // 4
    for i, t in enumerate(tl):
        r, c = divmod(i, 4)
        x = M + 130 + c * seg2
        y = ty2 + 3 + r * 15
        d.text((x, y), t["time"], font=SANS_B(10), fill=AMBER)
        d.text((x + 38, y), t["label"], font=SANS(10),
               fill=(255, 255, 255))

    # ---- DATE CHECK red box
    dy = 930
    d.rectangle([0, dy, W, dy + 64], fill=(255, 243, 205))
    d.rectangle([0, dy, W, dy + 64], outline=RED, width=2)
    d.text((M, dy + 5), "DATE CHECK \u2014 LEFT OUT ON PURPOSE (NOT 22 NOVEMBER):",
           font=SANS_B(11), fill=RED)
    dc = ("400-drone / 110-missile strike on Ukraine \u2014 19-20 Nov  \u00b7  "
          "ICJ: Myanmar guilty of Rohingya genocide \u2014 19 Nov  \u00b7  "
          "Nigeria boat capsizes, 24 dead \u2014 20 Nov  \u00b7  "
          "Sparta II drone strike itself \u2014 21 Nov  \u00b7  "
          "FIFA names UK 2035 Women's World Cup host \u2014 23 Nov")
    f, lines = fit_lines(d, dc, SANS(11), W - 2 * M, 2, bold=False)
    yy = dy + 21
    for ln in lines:
        d.text((M, yy), ln, font=f, fill=INK)
        yy += f.size + 1
    d.text((M, dy + 50), "NOT DECIDED ON SUNDAY: COP31 final vote  \u00b7  "
           "Gaza aid crossings",
           font=SANS_B(10), fill=RED)

    # ---- footer
    fy = 1000
    d.text((M, fy), "All 33 stories happened or were first reported Sunday "
           "22 Nov 2026 \u00b7 Sources: Reuters, AP, BBC, Al Jazeera, CNN, "
           "Ukrainian Air Force, RFE/RL \u00b7 Claims marked CLAIM.",
           font=SANS(10), fill=MUTED)
    return img


def main():
    img = draw()
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
