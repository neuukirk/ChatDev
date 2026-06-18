# Old Body Style — Render My Ride (v1 prototype)

A generative synthwave / 90s poster studio. Upload a photo of your ride (or hit
"Surprise me") and get a retro poster: gradient sky, scanline sun, perspective
grid, your ride as a neon-framed hero, chrome type, and film grain.

This is an early prototype built to explore an autonomous content + commerce
brand. Status: working v1. (The product direction is under review.)

## Run it

```bash
cd old-body-style
pip install -r requirements.txt
python -m render_my_ride.app
# open http://127.0.0.1:5000
```

## Business model (demonstrated in the app)

- Free, watermarked preview for any render.
- Paid unlock ($12 placeholder) delivers the clean, high-res, print-ready file.
- Checkout is mocked in v1; the purchase gate and delivery are real.

## Layout

```
old-body-style/
  render_my_ride/
    engine.py      # the generative poster engine (Pillow, deterministic by seed)
    palettes.py    # synthwave color schemes
    app.py         # self-serve Flask web app (upload, preview, buy, download)
  examples/        # sample renders
  tests/           # engine + web-flow tests
```

## Tests

```bash
cd old-body-style
python -m unittest discover
```
