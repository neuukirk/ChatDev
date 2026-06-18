"""Render a shareable synthwave result card as a PNG.

Stateless: everything needed is passed in, so the card can be generated from URL
params and dropped straight into a social post.
"""

from __future__ import annotations

import io
import os
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

SIZE = (1080, 1080)
BG_TOP = (26, 11, 58)
BG_HORIZON = (255, 94, 148)
GROUND = (8, 4, 24)
CYAN = (0, 234, 255)
PINK = (255, 45, 181)
GREEN = (57, 255, 136)
YELLOW = (255, 210, 63)
TEXT = (243, 233, 255)

GRADE_COLORS = {"S": GREEN, "A": GREEN, "B": CYAN, "C": YELLOW, "D": PINK}

_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONTS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _lerp(c1, c2, t):
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3))


def _center(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def _text_center(draw, cx, y, text, font, fill):
    w, _ = _center(draw, text, font)
    draw.text((cx - w // 2, y), text, font=font, fill=fill)


def render_card(grade: str, score: int, accuracy: int, combo: int,
                initials: str, track: str = "", day: int = 0) -> Image.Image:
    w, h = SIZE
    horizon = int(h * 0.46)
    img = Image.new("RGB", SIZE)

    # Sky + ground.
    strip = Image.new("RGB", (1, horizon))
    for y in range(horizon):
        strip.putpixel((0, y), _lerp(BG_TOP, BG_HORIZON, y / max(1, horizon - 1)))
    img.paste(strip.resize((w, horizon)), (0, 0))
    g2 = Image.new("RGB", (1, h - horizon))
    for y in range(h - horizon):
        g2.putpixel((0, y), _lerp((40, 10, 60), GROUND, y / max(1, h - horizon - 1)))
    img.paste(g2.resize((w, h - horizon)), (0, horizon))

    draw = ImageDraw.Draw(img)

    # Perspective grid on the ground.
    vp = (w // 2, horizon)
    for x in range(-w, 2 * w + 1, 80):
        draw.line([(x, h), vp], fill=(0, 234, 255), width=1)
    n = 14
    for i in range(1, n + 1):
        t = i / n
        y = int(horizon + (h - horizon) * (t * t))
        draw.line([(0, y), (w, y)], fill=(0, 180, 220), width=1)

    # Sun.
    d = int(w * 0.34)
    sun = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    sg = Image.new("RGB", (1, d))
    for y in range(d):
        sg.putpixel((0, y), _lerp((255, 222, 89), (255, 64, 129), y / max(1, d - 1)))
    mask = Image.new("L", (d, d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
    sun.paste(sg.resize((d, d)), (0, 0), mask)
    img.paste(sun, ((w - d) // 2, horizon - int(d * 0.72)), sun)

    # Branding.
    _text_center(draw, w // 2, 48, "BEATGRID", _font(64), CYAN)
    if day:
        _text_center(draw, w // 2, 122, f"DAILY #{day}", _font(30), TEXT)

    # Grade.
    grade = grade if grade in GRADE_COLORS else "D"
    gfont = _font(300)
    gcolor = GRADE_COLORS[grade]
    gw, gh = _center(draw, grade, gfont)
    gx, gy = w // 2 - gw // 2, horizon - 150
    draw.text((gx - 6, gy), grade, font=gfont, fill=PINK)
    draw.text((gx + 6, gy), grade, font=gfont, fill=CYAN)
    draw.text((gx, gy), grade, font=gfont, fill=gcolor)

    # Stats panel.
    _text_center(draw, w // 2, h - 360, f"{accuracy}% ACCURACY", _font(64), TEXT)
    _text_center(draw, w // 2, h - 270, f"SCORE {score}", _font(48), CYAN)
    _text_center(draw, w // 2, h - 200, f"MAX COMBO {combo}", _font(40), PINK)
    if track:
        _text_center(draw, w // 2, h - 130, track[:40], _font(34), TEXT)

    # Initials badge.
    initials = "".join(ch for ch in (initials or "AAA").upper() if ch.isalpha())[:3] or "AAA"
    _text_center(draw, w // 2, h - 78, f"— {initials} —", _font(38), YELLOW)

    # Frame.
    draw.rectangle([10, 10, w - 11, h - 11], outline=PINK, width=5)
    return img


def render_png(**kwargs) -> bytes:
    buf = io.BytesIO()
    render_card(**kwargs).save(buf, format="PNG")
    return buf.getvalue()
