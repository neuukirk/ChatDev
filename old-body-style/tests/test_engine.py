"""Tests for the Render My Ride engine and web flow.

Run from old-body-style/:  python -m unittest discover
"""

import io
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PIL import Image  # noqa: E402

from render_my_ride.engine import POSTER_SIZE, render_poster, render_to_png_bytes  # noqa: E402


def _fake_photo() -> bytes:
    img = Image.new("RGB", (640, 400), (120, 130, 150))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


class EngineTests(unittest.TestCase):
    def test_generative_render_size(self):
        img, meta = render_poster(seed=7, watermark=False)
        self.assertEqual(img.size, POSTER_SIZE)
        self.assertEqual(meta["seed"], 7)
        self.assertFalse(meta["has_photo"])

    def test_same_seed_is_deterministic(self):
        a, _ = render_poster(seed=123, palette_name="miami", watermark=False)
        b, _ = render_poster(seed=123, palette_name="miami", watermark=False)
        self.assertEqual(a.tobytes(), b.tobytes())

    def test_different_seed_differs(self):
        a, _ = render_poster(seed=1, palette_name="miami", watermark=False)
        b, _ = render_poster(seed=2, palette_name="miami", watermark=False)
        self.assertNotEqual(a.tobytes(), b.tobytes())

    def test_photo_path_renders(self):
        img, meta = render_poster(image_bytes=_fake_photo(), seed=5, watermark=False)
        self.assertEqual(img.size, POSTER_SIZE)
        self.assertTrue(meta["has_photo"])

    def test_watermark_changes_output(self):
        clean, _ = render_poster(seed=9, palette_name="vapor", watermark=False)
        marked, _ = render_poster(seed=9, palette_name="vapor", watermark=True)
        self.assertNotEqual(clean.tobytes(), marked.tobytes())

    def test_png_bytes(self):
        data, _ = render_to_png_bytes(seed=3, watermark=False)
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")


class WebFlowTests(unittest.TestCase):
    def setUp(self):
        from render_my_ride.app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_ok(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_purchase_gate(self):
        r = self.client.post("/render", data={"surprise": "1", "palette": "toxic"})
        self.assertEqual(r.status_code, 302)
        oid = r.headers["Location"].rsplit("/", 1)[-1]
        self.assertEqual(self.client.get(f"/image/{oid}/preview").status_code, 200)
        self.assertEqual(self.client.get(f"/image/{oid}/full").status_code, 402)
        self.assertEqual(self.client.get(f"/buy/{oid}").status_code, 302)
        self.assertEqual(self.client.get(f"/image/{oid}/full").status_code, 200)


if __name__ == "__main__":
    unittest.main()
