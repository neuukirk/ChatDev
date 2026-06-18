# BEATGRID

**A daily retro rhythm game with a cross-linked sound shop.** One site, two
surfaces, one flywheel: the free daily game is the marketing, the shop is the
revenue, and both run on the same retro-audio engine.

Part of the Old Body Style Arcade. This is the v1 prototype.

---

## The idea

- **Play (free, viral):** a new rhythm challenge every day, the same for
  everyone (Wordle cadence). The chart is generated from the date, so a fresh
  game appears daily with no manual work.
- **Compete + share (growth loop):** classic 3-letter arcade initials on a daily
  leaderboard, plus a generated synthwave **share-card image** to post.
- **Sound Shop (the money):** original retro track packs sold as digital goods.
  Free in-browser previews, paid unlock of the full downloadable pack.
- **The wire between them:** today's beat comes from a real pack, and the game
  links straight to it ("Get the pack"). Daily play converts into shop sales.

The audio is synthesized in the browser with the Web Audio API. The same track
data (BPM + 16-step kick/snare/hat/bass patterns) drives both the music and the
falling notes, so gameplay and sound are always in sync. No audio files, no
external services, no third-party IP.

---

## Run it

No build step. Python 3.8+.

```bash
cd beatgrid
pip install -r requirements.txt
python -m beatgrid.app
# open http://127.0.0.1:5000
```

- Play the daily game: hit **D F J K** (or tap the lanes) as notes reach the line.
- Browse the **Sound Shop**, preview tracks, "buy" a pack (mock checkout), then
  download it. The download is gated until purchase.

---

## How it makes money

- **Pack sales** (digital goods, the core).
- **No-ads / pro** on the game later (extra modes, full back-catalog of dailies).
- **Cosmetic themes** that are themselves mini packs.

Checkout is mocked in this v1 (`/buy/<pack>` flips an in-memory flag). The
purchase gate and gated download are real, so the model is fully demonstrable.
Production swaps the in-memory store for a database and Stripe webhooks.

---

## Layout

```
beatgrid/
  beatgrid/
    catalog.py        # the sound catalog (packs + tracks/patterns)
    daily.py          # deterministic daily selection from the date
    store.py          # SQLite daily leaderboard
    sharecard.py      # synthwave result-card PNG (Pillow)
    app.py            # Flask app: game + shop + leaderboard + share card
    static/
      game.js         # Web Audio synth + 4-lane rhythm game + shop preview
      style.css       # synthwave UI
  tests/              # catalog, daily, leaderboard, share-card, web-flow tests
  requirements.txt
```

Run the tests:

```bash
cd beatgrid
python -m unittest discover
```

---

## What the v1 proves

A playable daily game with a leaderboard and a shareable result card, plus a
working storefront that cross-sells from the game, all from one shared engine.
The next steps are real checkout (Stripe), a daily auto-post to social, and
growing the pack catalog (the content the whole flywheel runs on).
