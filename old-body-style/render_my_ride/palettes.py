"""Color palettes for the Old Body Style poster engine.

Each palette is a synthwave / 90s-nostalgia scheme. Keys:
  sky_top      top of the sky gradient
  sky_horizon  sky color at the horizon
  ground_top   ground color just under the horizon
  ground_bottom bottom of the poster
  sun_top      top of the sun gradient
  sun_bottom   bottom of the sun gradient
  grid         neon grid line color
  accent       neon accent (frames, silhouette)
  duo_dark     dark tone for the duotone treatment of an uploaded photo
  duo_light    light tone for the duotone treatment
"""

PALETTES = {
    "miami": {
        "sky_top": (26, 11, 58),
        "sky_horizon": (255, 94, 148),
        "ground_top": (40, 10, 60),
        "ground_bottom": (8, 4, 24),
        "sun_top": (255, 222, 89),
        "sun_bottom": (255, 64, 129),
        "grid": (0, 234, 255),
        "accent": (255, 0, 170),
        "duo_dark": (35, 8, 60),
        "duo_light": (0, 234, 255),
    },
    "sunset": {
        "sky_top": (18, 14, 48),
        "sky_horizon": (255, 140, 66),
        "ground_top": (48, 16, 52),
        "ground_bottom": (10, 6, 20),
        "sun_top": (255, 236, 120),
        "sun_bottom": (255, 78, 66),
        "grid": (255, 86, 200),
        "accent": (255, 196, 0),
        "duo_dark": (40, 10, 40),
        "duo_light": (255, 176, 64),
    },
    "vapor": {
        "sky_top": (22, 8, 54),
        "sky_horizon": (123, 92, 255),
        "ground_top": (30, 12, 64),
        "ground_bottom": (6, 4, 22),
        "sun_top": (180, 255, 240),
        "sun_bottom": (255, 110, 199),
        "grid": (0, 255, 178),
        "accent": (0, 229, 255),
        "duo_dark": (28, 10, 58),
        "duo_light": (0, 255, 198),
    },
    "toxic": {
        "sky_top": (10, 20, 30),
        "sky_horizon": (57, 255, 136),
        "ground_top": (10, 30, 28),
        "ground_bottom": (4, 10, 10),
        "sun_top": (224, 255, 120),
        "sun_bottom": (0, 200, 120),
        "grid": (0, 255, 102),
        "accent": (170, 255, 0),
        "duo_dark": (6, 28, 22),
        "duo_light": (120, 255, 140),
    },
}

PALETTE_NAMES = list(PALETTES.keys())
