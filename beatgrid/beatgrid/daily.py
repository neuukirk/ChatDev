"""Deterministic daily selection.

Everyone gets the same track and chart on the same calendar day (Wordle style),
with no manual work: the day's index is derived from the date.
"""

from __future__ import annotations

import datetime
from typing import Dict, Optional

from . import catalog

EPOCH = datetime.date(2024, 1, 1)


def day_number(today: Optional[datetime.date] = None) -> int:
    today = today or datetime.date.today()
    return (today - EPOCH).days


def daily_track(today: Optional[datetime.date] = None) -> Dict:
    today = today or datetime.date.today()
    tracks = catalog.all_tracks()
    idx = day_number(today) % len(tracks)
    return tracks[idx]


def daily_payload(today: Optional[datetime.date] = None) -> Dict:
    """The JSON the front-end needs to play today's game."""
    today = today or datetime.date.today()
    track = daily_track(today)
    return {
        "date": today.isoformat(),
        "day": day_number(today),
        "track_name": track["name"],
        "pack_id": track["pack_id"],
        "pack_name": track["pack_name"],
        "bpm": track["bpm"],
        "bars": track["bars"],
        "steps": catalog.STEPS,
        "root_hz": catalog.ROOT_HZ,
        "patterns": {
            "kick": track["kick"],
            "snare": track["snare"],
            "hat": track["hat"],
            "bass": track["bass"],
        },
    }
