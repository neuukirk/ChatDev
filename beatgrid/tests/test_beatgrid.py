"""Tests for BEATGRID. Run from beatgrid/:  python -m unittest discover"""

import datetime
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Use an isolated DB for tests before importing anything that touches the store.
_TMP_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP_DB.close()
os.environ["BEATGRID_DB"] = _TMP_DB.name

from beatgrid import catalog, daily, store  # noqa: E402


class CatalogTests(unittest.TestCase):
    def test_patterns_are_16_steps(self):
        for track in catalog.all_tracks():
            for key in ("kick", "snare", "hat", "bass"):
                self.assertEqual(len(track[key]), catalog.STEPS,
                                 f"{track['name']} {key} wrong length")

    def test_every_track_traces_to_a_pack(self):
        for track in catalog.all_tracks():
            self.assertEqual(catalog.get_pack(track["pack_id"])["id"], track["pack_id"])

    def test_each_track_has_some_notes(self):
        for track in catalog.all_tracks():
            notes = (sum(track["kick"]) + sum(track["snare"]) + sum(track["hat"])
                     + sum(1 for b in track["bass"] if b != -1))
            self.assertGreater(notes, 0)


class DailyTests(unittest.TestCase):
    def test_same_day_same_track(self):
        day = datetime.date(2026, 6, 18)
        self.assertEqual(daily.daily_track(day)["name"], daily.daily_track(day)["name"])

    def test_rotation_changes_over_time(self):
        names = {daily.daily_track(datetime.date(2024, 1, 1)
                 + datetime.timedelta(days=i))["name"] for i in range(len(catalog.all_tracks()))}
        self.assertEqual(len(names), len(catalog.all_tracks()))  # full cycle hits all

    def test_payload_shape(self):
        p = daily.daily_payload(datetime.date(2026, 6, 18))
        for key in ("date", "day", "track_name", "pack_id", "bpm", "bars", "patterns"):
            self.assertIn(key, p)
        self.assertEqual(set(p["patterns"]), {"kick", "snare", "hat", "bass"})


class WebTests(unittest.TestCase):
    def setUp(self):
        from beatgrid.app import app, PURCHASED
        app.config["TESTING"] = True
        PURCHASED.clear()
        store.init_db()
        with store._conn() as conn:  # isolate each test's leaderboard
            conn.execute("DELETE FROM scores")
        self.client = app.test_client()

    def test_home_and_assets(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/static/game.js").status_code, 200)
        self.assertEqual(self.client.get("/static/style.css").status_code, 200)

    def test_api_daily_json(self):
        r = self.client.get("/api/daily")
        self.assertEqual(r.status_code, 200)
        self.assertIn("patterns", r.get_json())

    def test_shop_and_pack(self):
        self.assertEqual(self.client.get("/shop").status_code, 200)
        self.assertEqual(self.client.get("/shop/midnight-drive").status_code, 200)
        self.assertEqual(self.client.get("/shop/nope").status_code, 404)

    def test_download_gated_then_unlocked(self):
        self.assertEqual(self.client.get("/download/midnight-drive").status_code, 402)
        self.assertEqual(self.client.get("/buy/midnight-drive").status_code, 302)
        r = self.client.get("/download/midnight-drive")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data)["id"], "midnight-drive")

    def test_score_submit_and_leaderboard(self):
        r = self.client.post("/api/score", json={
            "initials": "axn!", "score": 5000, "accuracy": 88, "combo": 40, "grade": "A",
        })
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["rank"], 1)
        self.assertEqual(data["leaderboard"][0]["initials"], "AXN")  # sanitized, uppercased
        lb = self.client.get("/api/leaderboard").get_json()
        self.assertGreaterEqual(lb["players"], 1)

    def test_higher_score_ranks_first(self):
        self.client.post("/api/score", json={"initials": "LOW", "score": 10,
                                             "accuracy": 10, "combo": 1, "grade": "D"})
        r = self.client.post("/api/score", json={"initials": "TOP", "score": 9000,
                                                 "accuracy": 99, "combo": 99, "grade": "S"})
        self.assertEqual(r.get_json()["leaderboard"][0]["initials"], "TOP")

    def test_share_card_png(self):
        r = self.client.get("/share-card.png?grade=S&score=8000&acc=97&combo=80&initials=AXN&day=12&track=Neon")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.mimetype, "image/png")
        self.assertEqual(r.data[:8], b"\x89PNG\r\n\x1a\n")


class StoreTests(unittest.TestCase):
    def test_initials_sanitized(self):
        self.assertEqual(store.clean_initials("a1b2c3d"), "ABC")
        self.assertEqual(store.clean_initials(""), "AAA")


if __name__ == "__main__":
    unittest.main()
