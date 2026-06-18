"""Tests for BEATGRID. Run from beatgrid/:  python -m unittest discover"""

import datetime
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from beatgrid import catalog, daily  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
