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
    url_for,
)

from . import catalog, daily

app = Flask(__name__)

# In-memory purchases. A real build swaps this for a DB + Stripe webhooks.
PURCHASED: set = set()

PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} — BEATGRID</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head><body>
<header><a class="logo" href="{{ url_for('home') }}">BEAT<span>GRID</span></a>
<nav><a href="{{ url_for('home') }}">Play</a><a href="{{ url_for('shop') }}">Sound Shop</a></nav>
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


def _render(title, body, **ctx):
    inner = render_template_string(body, **ctx)
    return render_template_string(PAGE, title=title, body=inner)


@app.route("/")
def home():
    payload = daily.daily_payload()
    return _render("Play", HOME_BODY, daily_json=json.dumps(payload))


@app.route("/api/daily")
def api_daily():
    return jsonify(daily.daily_payload())


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
