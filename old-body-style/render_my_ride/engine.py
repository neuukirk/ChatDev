"""The Old Body Style generative poster engine.

Turns an uploaded vehicle photo (or nothing at all) into a synthwave / 90s
poster: gradient sky, scanline sun, perspective grid, the ride as a neon-framed
hero, brand type, and film grain. Deterministic from a seed, so every render is
reproducible and every seed is a different poster.

Pure local processing. No external services.
"""

from __future__ import annotations

import io
import os
import random
from typing import Optional, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

from .palettes import PALETTES, PALETTE_NAMES

POSTER_SIZE = (1080, 1350)
HORIZON_RATIO = 0.60

Color = Tuple[int, int, int]

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _lerp(c1: Color, c2: Color, t: float) -> Color:
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3))


def _vertical_gradient(w: int, h: int, top: Color, bottom: Color) -> Image.Image:
    strip = Image.new("RGB", (1, h))
    for y in range(h):
        strip.putpixel((0, y), _lerp(top, bottom, y / max(1, h - 1)))
    return strip.resize((w, h))


def _draw_sky(rng: random.Random, palette: dict) -> Image.Image:
    w, h = POSTER_SIZE
    horizon = int(h * HORIZON_RATIO)
    img = Image.new("RGB", POSTER_SIZE)
    sky = _vertical_gradient(w, horizon, palette["sky_top"], palette["sky_horizon"])
    ground = _vertical_gradient(w, h - horizon, palette["ground_top"], palette["ground_bottom"])
    img.paste(sky, (0, 0))
    img.paste(ground, (0, horizon))

    # Stars in the upper sky.
    draw = ImageDraw.Draw(img)
    for _ in range(rng.randint(60, 110)):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, int(horizon * 0.72))
        b = rng.randint(120, 255)
        draw.point((x, y), fill=(b, b, b))
    return img


def _make_sun(rng: random.Random, palette: dict, diameter: int) -> Image.Image:
    """A retrowave sun: vertical gradient disc with widening scanline gaps."""
    grad = _vertical_gradient(diameter, diameter, palette["sun_top"], palette["sun_bottom"])
    sun = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter - 1, diameter - 1), fill=255)
    sun.paste(grad, (0, 0), mask)

    # Cut horizontal stripes across the lower portion, getting thicker downward.
    start = int(diameter * 0.52)
    y = start
    gap = 4
    stripe = 3
    while y < diameter:
        for sy in range(y, min(y + stripe, diameter)):
            for x in range(diameter):
                sun.putpixel((x, sy), (0, 0, 0, 0))
        y += stripe + gap
        stripe += 2  # thicker cuts lower down
    return sun


def _draw_grid(img: Image.Image, palette: dict) -> None:
    w, h = POSTER_SIZE
    horizon = int(h * HORIZON_RATIO)
    vp = (w // 2, horizon)
    grid = palette["grid"]
    layer = Image.new("RGBA", POSTER_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Converging vertical lines.
    step = 90
    for x in range(-w, 2 * w + 1, step):
        draw.line([(x, h), vp], fill=grid + (180,), width=2)

    # Horizontal lines, spaced wider toward the bottom (perspective).
    n = 16
    for i in range(1, n + 1):
        t = i / n
        y = int(horizon + (h - horizon) * (t * t))
        draw.line([(0, y), (w, y)], fill=grid + (150,), width=2)

    # Fade the grid out near the horizon for depth.
    fade = Image.new("L", POSTER_SIZE, 0)
    fdraw = ImageDraw.Draw(fade)
    for y in range(horizon, h):
        a = int(255 * min(1.0, (y - horizon) / (h - horizon) * 1.6))
        fdraw.line([(0, y), (w, y)], fill=a)
    r, g, b, a = layer.split()
    a = ImageChops.multiply(a, fade)
    layer = Image.merge("RGBA", (r, g, b, a))
    img.paste(layer, (0, 0), layer)


def _process_vehicle(image_bytes: bytes, palette: dict, target_w: int) -> Image.Image:
    """Duotone an uploaded photo and frame it like a glowing CRT panel."""
    photo = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    photo = ImageOps.exif_transpose(photo)
    photo = ImageOps.autocontrast(photo, cutoff=2)
    gray = ImageOps.grayscale(photo)
    duo = ImageOps.colorize(
        gray,
        black=palette["duo_dark"],
        white=palette["duo_light"],
        mid=palette["accent"],
    )

    ratio = target_w / duo.width
    target_h = max(1, int(duo.height * ratio))
    duo = duo.resize((target_w, target_h))

    # CRT scanlines over the photo.
    sl = ImageDraw.Draw(duo)
    for y in range(0, target_h, 3):
        sl.line([(0, y), (target_w, y)], fill=(0, 0, 0), width=1)

    # Neon frame.
    pad = 14
    framed = Image.new("RGB", (target_w + pad * 2, target_h + pad * 2), palette["ground_bottom"])
    framed.paste(duo, (pad, pad))
    fd = ImageDraw.Draw(framed)
    fd.rectangle([2, 2, framed.width - 3, framed.height - 3], outline=palette["accent"], width=5)
    fd.rectangle([pad - 4, pad - 4, framed.width - pad + 3, framed.height - pad + 3],
                 outline=palette["grid"], width=2)
    return framed


def _draw_truck(rng: random.Random, palette: dict, width: int) -> Image.Image:
    """A boxy OBS-style truck silhouette for renders with no uploaded photo."""
    w = width
    h = int(width * 0.5)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = palette["accent"]
    # Cab + bed (boxy), classic old-body-style proportions.
    d.rectangle([int(w * 0.06), int(h * 0.45), int(w * 0.94), int(h * 0.78)], fill=body)  # body
    d.polygon([(int(w * 0.30), int(h * 0.45)), (int(w * 0.40), int(h * 0.18)),
               (int(w * 0.74), int(h * 0.18)), (int(w * 0.80), int(h * 0.45))], fill=body)  # cab
    # Windows
    d.polygon([(int(w * 0.40), int(h * 0.43)), (int(w * 0.45), int(h * 0.24)),
               (int(w * 0.72), int(h * 0.24)), (int(w * 0.76), int(h * 0.43))],
              fill=palette["sky_top"])
    # Wheels
    for cx in (int(w * 0.26), int(w * 0.74)):
        r = int(h * 0.16)
        d.ellipse([cx - r, int(h * 0.70), cx + r, int(h * 0.70) + 2 * r], fill=(10, 10, 14))
        d.ellipse([cx - r // 2, int(h * 0.70) + r - r // 2,
                   cx + r // 2, int(h * 0.70) + r + r // 2], fill=palette["grid"])
    return img


def _chrome_text(draw: ImageDraw.ImageDraw, xy, text, font, palette) -> None:
    x, y = xy
    # Chromatic offsets for the retro look.
    draw.text((x - 4, y), text, font=font, fill=palette["accent"])
    draw.text((x + 4, y), text, font=font, fill=palette["grid"])
    draw.text((x, y), text, font=font, fill=(255, 255, 255))


def _centered(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def _add_grain(rng: random.Random, img: Image.Image, amount: float = 0.07) -> Image.Image:
    # Build noise from the seeded RNG (at reduced res for speed) so renders are
    # reproducible. Image.effect_noise has its own uncontrollable RNG.
    sw, sh = POSTER_SIZE[0] // 3, POSTER_SIZE[1] // 3
    noise = Image.frombytes("L", (sw, sh), rng.randbytes(sw * sh))
    noise = noise.convert("RGB").resize(POSTER_SIZE)
    return Image.blend(img, noise, amount)


def _watermark(img: Image.Image) -> None:
    w, h = POSTER_SIZE
    layer = Image.new("RGBA", POSTER_SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    font = _load_font(34)
    text = "OLD BODY STYLE  •  PREVIEW   "
    for row, y in enumerate(range(0, h, 120)):
        offset = -((row % 2) * 240)
        d.text((offset, y), text * 3, font=font, fill=(255, 255, 255, 38))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))


def render_poster(
    image_bytes: Optional[bytes] = None,
    seed: Optional[int] = None,
    title: str = "OLD BODY STYLE",
    subtitle: str = "RENDER MY RIDE",
    palette_name: Optional[str] = None,
    watermark: bool = True,
) -> Tuple[Image.Image, dict]:
    """Render a poster. Returns (image, metadata)."""
    if seed is None:
        seed = random.randint(0, 2 ** 31 - 1)
    rng = random.Random(seed)

    if palette_name not in PALETTES:
        palette_name = rng.choice(PALETTE_NAMES)
    palette = PALETTES[palette_name]

    w, h = POSTER_SIZE
    horizon = int(h * HORIZON_RATIO)

    img = _draw_sky(rng, palette)

    # Sun, sitting on the horizon.
    diameter = int(w * rng.uniform(0.42, 0.52))
    sun = _make_sun(rng, palette, diameter)
    sun_x = (w - diameter) // 2
    sun_y = horizon - int(diameter * 0.78)
    img.paste(sun, (sun_x, sun_y), sun)

    _draw_grid(img, palette)

    # Hero: the ride.
    if image_bytes:
        hero = _process_vehicle(image_bytes, palette, target_w=int(w * 0.70))
    else:
        hero = _draw_truck(rng, palette, width=int(w * 0.70))
    hero_x = (w - hero.width) // 2
    hero_y = horizon - int(hero.height * 0.50)
    if hero.mode == "RGBA":
        img.paste(hero, (hero_x, hero_y), hero)
    else:
        img.paste(hero, (hero_x, hero_y))

    img = _add_grain(rng, img)

    # Type.
    draw = ImageDraw.Draw(img)
    title_font = _load_font(96)
    sub_font = _load_font(40)
    tw, th = _centered(draw, title, title_font)
    _chrome_text(draw, ((w - tw) // 2, h - 230), title, title_font, palette)
    sw, sh = _centered(draw, subtitle, sub_font)
    draw.text(((w - sw) // 2, h - 110), subtitle, font=sub_font, fill=palette["grid"])

    # Border.
    ImageDraw.Draw(img).rectangle([8, 8, w - 9, h - 9], outline=palette["accent"], width=4)

    if watermark:
        _watermark(img)

    meta = {
        "seed": seed,
        "palette": palette_name,
        "has_photo": bool(image_bytes),
        "watermark": watermark,
        "size": POSTER_SIZE,
    }
    return img, meta


def render_to_png_bytes(**kwargs) -> Tuple[bytes, dict]:
    img, meta = render_poster(**kwargs)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue(), meta
