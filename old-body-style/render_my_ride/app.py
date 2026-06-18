"""Render My Ride: the self-serve web app for Old Body Style.

Flow: upload a photo of your ride (or hit "Surprise me"), get a free watermarked
preview, then buy the clean high-res poster. Checkout is mocked for this v1; the
purchase gate and delivery are real so the business model is demonstrable.

Run:
    cd old-body-style
    python -m render_my_ride.app
    # open http://127.0.0.1:5000
"""

from __future__ import annotations

import os
import uuid

from flask import (
    Flask,
    Response,
    abort,
    redirect,
    render_template_string,
    request,
    send_file,
    url_for,
)

from .engine import POSTER_SIZE, render_poster
from .palettes import PALETTE_NAMES

PRICE = "$12"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024  # 12 MB uploads

# In-memory order book. A real build swaps this for a database.
ORDERS: dict = {}


def _save(img, order_id, kind):
    path = os.path.join(OUTPUT_DIR, f"{order_id}_{kind}.png")
    img.save(path, format="PNG")
    return path


BASE_CSS = """
:root { --bg:#0b0420; --panel:#160a33; --pink:#ff2db5; --cyan:#00eaff; --text:#f3e9ff; }
* { box-sizing:border-box; }
body { margin:0; font-family:'Segoe UI',system-ui,sans-serif; color:var(--text);
  background:radial-gradient(circle at 50% -10%, #3a0f5e 0%, var(--bg) 55%); min-height:100vh; }
.wrap { max-width:980px; margin:0 auto; padding:28px 20px 60px; }
.brand { font-size:46px; font-weight:800; letter-spacing:3px;
  background:linear-gradient(90deg,var(--cyan),var(--pink)); -webkit-background-clip:text;
  background-clip:text; color:transparent; text-align:center; margin:6px 0 0; }
.tag { text-align:center; color:var(--cyan); letter-spacing:6px; font-size:13px; margin:2px 0 26px; }
.panel { background:rgba(22,10,51,.75); border:1px solid rgba(0,234,255,.25);
  border-radius:14px; padding:22px; box-shadow:0 0 40px rgba(255,45,181,.12); }
label { display:block; font-size:13px; color:var(--cyan); margin:14px 0 6px; letter-spacing:1px; }
input[type=file], select { width:100%; padding:10px; background:#0d0526; color:var(--text);
  border:1px solid rgba(0,234,255,.3); border-radius:8px; }
.row { display:flex; gap:14px; flex-wrap:wrap; }
.row > div { flex:1; min-width:200px; }
.btn { display:inline-block; cursor:pointer; border:0; border-radius:10px; padding:14px 22px;
  font-weight:700; letter-spacing:1px; color:#0b0420; text-decoration:none;
  background:linear-gradient(90deg,var(--cyan),var(--pink)); }
.btn.ghost { background:transparent; color:var(--cyan); border:1px solid var(--cyan); }
.actions { margin-top:20px; display:flex; gap:12px; flex-wrap:wrap; }
.poster { width:100%; max-width:420px; border-radius:10px; display:block; margin:0 auto;
  box-shadow:0 10px 50px rgba(0,0,0,.6); }
.price { font-size:30px; font-weight:800; color:var(--pink); }
.muted { color:#b9a8e0; font-size:14px; line-height:1.5; }
.center { text-align:center; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; margin-top:18px; }
.grid img { width:100%; border-radius:8px; }
"""

HOME = """
<!doctype html><html><head><meta charset="utf-8"><title>Old Body Style — Render My Ride</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{{ css }}</style></head><body><div class="wrap">
  <h1 class="brand">OLD BODY STYLE</h1>
  <div class="tag">RENDER MY RIDE</div>
  <div class="panel">
    <form action="{{ url_for('render') }}" method="post" enctype="multipart/form-data">
      <label>Photo of your ride (optional)</label>
      <input type="file" name="photo" accept="image/*">
      <div class="row">
        <div>
          <label>Vibe</label>
          <select name="palette">
            <option value="">Random</option>
            {% for p in palettes %}<option value="{{ p }}">{{ p|capitalize }}</option>{% endfor %}
          </select>
        </div>
        <div>
          <label>Seed (optional)</label>
          <input type="file" style="display:none">
          <input name="seed" placeholder="leave blank for random" style="width:100%;padding:10px;
            background:#0d0526;color:var(--text);border:1px solid rgba(0,234,255,.3);border-radius:8px;">
        </div>
      </div>
      <div class="actions">
        <button class="btn" type="submit">Render my ride</button>
        <button class="btn ghost" type="submit" name="surprise" value="1">Surprise me</button>
      </div>
    </form>
    <p class="muted" style="margin-top:18px;">Free watermarked preview. Clean high-res poster is {{ price }}.</p>
  </div>

  {% if gallery %}
  <h3 style="margin-top:34px;color:var(--cyan);letter-spacing:2px;">RECENT DROPS</h3>
  <div class="grid">
    {% for gid in gallery %}<a href="{{ url_for('poster', order_id=gid) }}">
      <img src="{{ url_for('image', order_id=gid, kind='preview') }}"></a>{% endfor %}
  </div>
  {% endif %}
</div></body></html>
"""

RESULT = """
<!doctype html><html><head><meta charset="utf-8"><title>Your poster — Old Body Style</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{{ css }}</style></head><body><div class="wrap">
  <h1 class="brand">OLD BODY STYLE</h1>
  <div class="tag">RENDER MY RIDE</div>
  <div class="panel">
    <img class="poster" src="{{ url_for('image', order_id=oid, kind=('full' if order.purchased else 'preview')) }}">
    <div class="center" style="margin-top:18px;">
      {% if order.purchased %}
        <p class="muted">Purchased. This is your clean high-res poster ({{ size }}).</p>
        <a class="btn" href="{{ url_for('image', order_id=oid, kind='full') }}" download>Download high-res</a>
      {% else %}
        <div class="price">{{ price }}</div>
        <p class="muted">Preview is watermarked. Buy to unlock the clean, high-res, print-ready file.</p>
        <div class="actions center" style="justify-content:center;">
          <a class="btn" href="{{ url_for('buy', order_id=oid) }}">Buy clean poster ({{ price }})</a>
          <a class="btn ghost" href="{{ url_for('home') }}">Make another</a>
        </div>
      {% endif %}
      <p class="muted" style="margin-top:16px;">Palette: {{ order.meta.palette }} · Seed: {{ order.meta.seed }}</p>
    </div>
  </div>
</div></body></html>
"""


@app.route("/")
def home():
    gallery = list(ORDERS.keys())[-8:][::-1]
    return render_template_string(HOME, css=BASE_CSS, palettes=PALETTE_NAMES,
                                  price=PRICE, gallery=gallery)


@app.route("/render", methods=["POST"])
def render():
    photo_bytes = None
    if not request.form.get("surprise"):
        f = request.files.get("photo")
        if f and f.filename:
            photo_bytes = f.read()

    palette = request.form.get("palette") or None
    seed_raw = (request.form.get("seed") or "").strip()
    seed = int(seed_raw) if seed_raw.isdigit() else None

    order_id = uuid.uuid4().hex[:10]
    try:
        preview_img, meta = render_poster(image_bytes=photo_bytes, seed=seed,
                                          palette_name=palette, watermark=True)
        full_img, _ = render_poster(image_bytes=photo_bytes, seed=meta["seed"],
                                    palette_name=meta["palette"], watermark=False)
    except Exception:
        abort(400, "Could not process that image. Try a standard JPG or PNG.")

    _save(preview_img, order_id, "preview")
    _save(full_img, order_id, "full")
    ORDERS[order_id] = {"meta": meta, "purchased": False}
    return redirect(url_for("poster", order_id=order_id))


@app.route("/poster/<order_id>")
def poster(order_id):
    order = ORDERS.get(order_id)
    if not order:
        abort(404)
    return render_template_string(RESULT, css=BASE_CSS, oid=order_id, order=order,
                                  price=PRICE, size="x".join(map(str, POSTER_SIZE)))


@app.route("/buy/<order_id>")
def buy(order_id):
    order = ORDERS.get(order_id)
    if not order:
        abort(404)
    # Mocked checkout. A real build redirects to Stripe and confirms via webhook.
    order["purchased"] = True
    return redirect(url_for("poster", order_id=order_id))


@app.route("/image/<order_id>/<kind>")
def image(order_id, kind):
    if kind not in ("preview", "full"):
        abort(404)
    order = ORDERS.get(order_id)
    if not order:
        abort(404)
    if kind == "full" and not order["purchased"]:
        return Response("Purchase required to access the clean high-res file.", status=402)
    path = os.path.join(OUTPUT_DIR, f"{order_id}_{kind}.png")
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="image/png")


def main():
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
