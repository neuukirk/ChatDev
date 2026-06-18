"""The BEATGRID sound catalog.

Each pack contains tracks. A track is a one-bar groove (16 steps) plus a BPM
and a bar count. The same data drives both the in-browser audio synthesis and
the falling-note chart, so the music and the gameplay are always in sync.

Pattern conventions:
  kick / snare / hat : list of 16 ints, 1 = hit, 0 = rest
  bass               : list of 16 ints, semitones above the root, -1 = rest
"""

from __future__ import annotations

from typing import Dict, List

ROOT_HZ = 55.0  # A1; bass freq = ROOT_HZ * 2 ** (semitone / 12)
STEPS = 16

PACKS: List[Dict] = [
    {
        "id": "midnight-drive",
        "name": "Midnight Drive",
        "blurb": "Synthwave grooves for neon-soaked highways.",
        "price": "$9",
        "tracks": [
            {
                "name": "Neon Highway",
                "bpm": 112,
                "bars": 12,
                "kick":  [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
                "hat":   [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                "bass":  [0, -1, 0, -1, 7, -1, 7, -1, 5, -1, 5, -1, 3, -1, 3, -1],
            },
            {
                "name": "Chrome Sunset",
                "bpm": 104,
                "bars": 12,
                "kick":  [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                "hat":   [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0],
                "bass":  [0, -1, -1, 0, -1, -1, 3, -1, 5, -1, -1, 5, -1, -1, 7, -1],
            },
        ],
    },
    {
        "id": "polygon-dreams",
        "name": "Polygon Dreams",
        "blurb": "Low-poly PS1-era loops with that foggy 32-bit haze.",
        "price": "$9",
        "tracks": [
            {
                "name": "Loading Screen",
                "bpm": 96,
                "bars": 12,
                "kick":  [1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                "hat":   [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                "bass":  [0, -1, 0, -1, -1, 0, -1, -1, 8, -1, 7, -1, 5, -1, 3, -1],
            },
            {
                "name": "Foggy Draw Distance",
                "bpm": 88,
                "bars": 12,
                "kick":  [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                "hat":   [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                "bass":  [0, -1, -1, -1, 3, -1, -1, -1, 5, -1, -1, -1, 10, -1, 7, -1],
            },
        ],
    },
    {
        "id": "arcade-floor",
        "name": "Arcade Floor",
        "blurb": "Upbeat cabinet anthems for high-score runs.",
        "price": "$11",
        "tracks": [
            {
                "name": "Insert Coin",
                "bpm": 128,
                "bars": 12,
                "kick":  [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
                "hat":   [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
                "bass":  [0, 0, -1, 0, 0, -1, 0, -1, 7, 7, -1, 7, 5, -1, 3, -1],
            },
            {
                "name": "High Score",
                "bpm": 120,
                "bars": 12,
                "kick":  [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
                "hat":   [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                "bass":  [0, -1, 3, -1, 5, -1, 7, -1, 8, -1, 7, -1, 5, -1, 3, -1],
            },
        ],
    },
]


def all_tracks() -> List[Dict]:
    """Flatten the catalog into an ordered list of track records.

    Each record carries its pack id/name so a track can be traced back to the
    pack it is sold in (this powers the daily game cross-sell).
    """
    flat: List[Dict] = []
    for pack in PACKS:
        for track in pack["tracks"]:
            record = dict(track)
            record["pack_id"] = pack["id"]
            record["pack_name"] = pack["name"]
            flat.append(record)
    return flat


def get_pack(pack_id: str) -> Dict:
    for pack in PACKS:
        if pack["id"] == pack_id:
            return pack
    raise KeyError(pack_id)
