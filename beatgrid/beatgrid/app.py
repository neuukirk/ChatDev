"""BEATGRID web app: a daily retro rhythm game plus a cross-linked sound shop.

The daily game is free and brings people back every day. The shop sells the
packs the daily tracks come from. Each day's game points at the pack its beat
belongs to, so play converts into sales. Checkout is mocked for this v1; the
purchase gate and gated download are real.

Run:
    cd beatgrid
    python -m beatgrid.app
    # open http://127.0.0.1:5000
"""

from __future__ import annotations

import json
import os

from flask import (
    Flask,
    Response,
    abort,
    jsonify,
    redirect,
    render_template_string,
    request,
    url_for,
)

from . import catalog, daily, sharecard, store

app = Flask(__name__)
store.init_db()

# In-memory purchases. A real build swaps this for a DB + Stripe webhooks.
PURCHASED: set = set()

PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} — BEATGRID</title>
<meta property="og:title" content="{{ og_title }}">
<meta property="og:description" content="{{ og_desc }}">
<meta property="og:image" content="{{ og_image }}">
<meta property="og:url" content="{{ og_url }}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head><body>
<header><a class="logo" href="{{ url_for('home') }}">BEAT<span>GRID</span></a>
<nav><a href="{{ url_for('home') }}">Play</a><a href="{{ url_for('arcade') }}">Arcade</a><a href="{{ url_for('shop') }}">Sound Shop</a></nav>
</header>
<main>{{ body|safe }}</main>
<footer>A new beat every day. Original retro-style audio. © Old Body Style Arcade.</footer>
</body></html>
"""

HOME_BODY = """
<section class="play">
  <h1>Today's Beat</h1>
  <p class="sub" id="track-meta">Loading…</p>
  <div id="game"></div>
  <div class="crosssell" id="crosssell"></div>
</section>
<script>window.BEATGRID_DAILY = {{ daily_json|safe }};</script>
<script src="{{ url_for('static', filename='game.js') }}"></script>
"""

SHOP_BODY = """
<section class="shop">
  <h1>Sound Shop</h1>
  <p class="sub">Original retro packs. Each daily beat comes from one of these.</p>
  <div class="grid">
  {% for pack in packs %}
    <a class="card" href="{{ url_for('pack_page', pack_id=pack.id) }}">
      <div class="card-art {{ pack.id }}"></div>
      <h3>{{ pack.name }}</h3>
      <p>{{ pack.blurb }}</p>
      <div class="row"><span class="price">{{ pack.price }}</span>
        <span class="count">{{ pack.tracks|length }} tracks
          {% if pack.id in purchased %}· owned{% endif %}</span></div>
    </a>
  {% endfor %}
  </div>
</section>
"""

PACK_BODY = """
<section class="pack">
  <a class="back" href="{{ url_for('shop') }}">← Sound Shop</a>
  <div class="pack-head">
    <div class="card-art big {{ pack.id }}"></div>
    <div>
      <h1>{{ pack.name }}</h1>
      <p class="sub">{{ pack.blurb }}</p>
      <div class="row">
        <span class="price">{{ pack.price }}</span>
        {% if owned %}
          <a class="btn" href="{{ url_for('download', pack_id=pack.id) }}">Download pack (.json)</a>
        {% else %}
          <a class="btn" href="{{ url_for('buy', pack_id=pack.id) }}">Buy pack ({{ pack.price }})</a>
        {% endif %}
      </div>
      {% if owned %}<p class="owned">Owned. Full pack unlocked.</p>
      {% else %}<p class="note">Preview the tracks below. Buying unlocks the full downloadable pack.</p>{% endif %}
    </div>
  </div>
  <ul class="tracklist">
  {% for t in pack.tracks %}
    <li><button class="play-btn" data-track="{{ loop.index0 }}">▶</button>
      <span>{{ t.name }}</span><span class="bpm">{{ t.bpm }} BPM</span></li>
  {% endfor %}
  </ul>
</section>
<script>window.BEATGRID_PACK = {{ pack_json|safe }};</script>
<script src="{{ url_for('static', filename='game.js') }}"></script>
<script>BEATGRID.initPackPreview();</script>
"""

ARCADE_BODY = """
<section class="play">
  <h1>Free Play Arcade</h1>
  <p class="sub">Play any track in the catalog. (The daily leaderboard lives on the Play tab.)</p>
  <div id="game"></div>
  <div class="crosssell" id="crosssell"></div>
  {% for pack in packs %}
    <h3 class="board-title">{{ pack.name }}</h3>
    <ul class="tracklist">
    {% for t in pack.tracks %}
      <li><button class="play-btn arcade-play" data-pack="{{ pack.id }}" data-track="{{ loop.index0 }}">▶</button>
        <span>{{ t.name }}</span><span class="bpm">{{ t.bpm }} BPM</span></li>
    {% endfor %}
    </ul>
  {% endfor %}
</section>
<script>window.BEATGRID_CATALOG = {{ catalog_json|safe }};</script>
<script src="{{ url_for('static', filename='game.js') }}"></script>
<script>BEATGRID.initArcade();</script>
"""

RESULT_BODY = """
<section class="play">
  <h1>BEATGRID Result</h1>
  <img class="resultcard" src="{{ card_url }}" alt="BEATGRID result card">
  <div class="actions">
    <a class="btn" href="{{ url_for('home') }}">Play today's beat</a>
    <a class="btn ghost" href="{{ url_for('shop') }}">Sound Shop</a>
  </div>
</section>
"""


def _render(title, body, og=None, **ctx):
    og = og or {}
    inner = render_template_string(body, **ctx)
    return render_template_string(
        PAGE, title=title, body=inner,
        og_title=og.get("title", "BEATGRID — A new beat every day"),
        og_desc=og.get("desc", "A daily retro rhythm game. Beat the leaderboard, share your score."),
        og_image=og.get("image", url_for("og_default", _external=True)),
        og_url=og.get("url", request.url),
    )


@app.route("/")
def home():
    payload = daily.daily_payload()
    return _render("Play", HOME_BODY, daily_json=json.dumps(payload))


@app.route("/api/daily")
def api_daily():
    return jsonify(daily.daily_payload())


@app.route("/api/score", methods=["POST"])
def api_score():
    body = request.get_json(silent=True) or {}
    today = daily.daily_payload()
    try:
        result = store.add_score(
            day=today["day"],
            date=today["date"],
            initials=str(body.get("initials", "AAA")),
            score=int(body.get("score", 0)),
            accuracy=int(body.get("accuracy", 0)),
            combo=int(body.get("combo", 0)),
            grade=str(body.get("grade", "D")),
        )
    except (TypeError, ValueError):
        return Response("Invalid score payload.", status=400)
    result["leaderboard"] = store.top_scores(today["day"])
    return jsonify(result)


@app.route("/api/leaderboard")
def api_leaderboard():
    today = daily.daily_payload()
    return jsonify({
        "day": today["day"],
        "players": store.player_count(today["day"]),
        "leaderboard": store.top_scores(today["day"]),
    })


@app.route("/og.png")
def og_default():
    return Response(sharecard.render_promo_png(), mimetype="image/png")


@app.route("/arcade")
def arcade():
    payload = {"packs": catalog.PACKS, "root_hz": catalog.ROOT_HZ, "steps": catalog.STEPS}
    return _render("Arcade", ARCADE_BODY, packs=catalog.PACKS,
                   catalog_json=json.dumps(payload))


@app.route("/result")
def result():
    a = request.args
    keys = ("grade", "score", "acc", "combo", "initials", "day", "track")
    params = {k: a.get(k) for k in keys if a.get(k) is not None}
    card_url = url_for("share_card", _external=True, **params)
    track_label = a.get("track") or "today's beat"
    og = {
        "title": f"BEATGRID #{a.get('day', '')} — {a.get('grade', '')} {a.get('acc', '')}%".strip(),
        "desc": f"Score {a.get('score', '0')} on {track_label}. Can you beat it?",
        "image": card_url,
        "url": request.url,
    }
    return _render("Result", RESULT_BODY, og=og, card_url=card_url)


@app.route("/share-card.png")
def share_card():
    a = request.args
    try:
        png = sharecard.render_png(
            grade=a.get("grade", "D"),
            score=max(0, min(int(a.get("score", 0)), 9_999_999)),
            accuracy=max(0, min(int(a.get("acc", 0)), 100)),
            combo=max(0, min(int(a.get("combo", 0)), 99_999)),
            initials=a.get("initials", "AAA"),
            track=a.get("track", ""),
            day=max(0, min(int(a.get("day", 0)), 99_999)),
        )
    except (TypeError, ValueError):
        return Response("Invalid card params.", status=400)
    return Response(png, mimetype="image/png")


@app.route("/shop")
def shop():
    return _render("Sound Shop", SHOP_BODY, packs=catalog.PACKS, purchased=PURCHASED)


@app.route("/shop/<pack_id>")
def pack_page(pack_id):
    try:
        pack = catalog.get_pack(pack_id)
    except KeyError:
        abort(404)
    return _render(pack["name"], PACK_BODY, pack=pack, owned=(pack_id in PURCHASED),
                   pack_json=json.dumps(pack))


@app.route("/buy/<pack_id>")
def buy(pack_id):
    try:
        catalog.get_pack(pack_id)
    except KeyError:
        abort(404)
    # Mocked checkout. A real build redirects to Stripe and confirms via webhook.
    PURCHASED.add(pack_id)
    return redirect(url_for("pack_page", pack_id=pack_id))


@app.route("/download/<pack_id>")
def download(pack_id):
    try:
        pack = catalog.get_pack(pack_id)
    except KeyError:
        abort(404)
    if pack_id not in PURCHASED:
        return Response("Purchase required to download this pack.", status=402)
    data = json.dumps(pack, indent=2)
    return Response(
        data,
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{pack_id}.json"'},
    )


def main():
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
