"""
intervals.py
純正律13音程のデータおよび対応する録音WAVファイル名の定義モジュール
"""

from typing import Dict, List

JUST_INTERVALS = [
    {"id": "unison",      "name": "完全1度 (Unison)",      "ratio": (1, 1),   "semitones": 0,  "filename": "unison.wav"},
    {"id": "minor_2nd",   "name": "短2度 (Minor 2nd)",     "ratio": (16, 15), "semitones": 1,  "filename": "minor_2nd.wav"},
    {"id": "major_2nd",   "name": "長2度 (Major 2nd)",     "ratio": (9, 8),   "semitones": 2,  "filename": "major_2nd.wav"},
    {"id": "minor_3rd",   "name": "短3度 (Minor 3rd)",     "ratio": (6, 5),   "semitones": 3,  "filename": "minor_3rd.wav"},
    {"id": "major_3rd",   "name": "長3度 (Major 3rd)",     "ratio": (5, 4),   "semitones": 4,  "filename": "major_3rd.wav"},
    {"id": "perfect_4th", "name": "完全4度 (Perfect 4th)",   "ratio": (4, 3),   "semitones": 5,  "filename": "perfect_4th.wav"},
    {"id": "tritone",     "name": "増4度/減5度 (Tritone)",  "ratio": (45, 32), "semitones": 6,  "filename": "tritone.wav"},
    {"id": "perfect_5th", "name": "完全5度 (Perfect 5th)",   "ratio": (3, 2),   "semitones": 7,  "filename": "perfect_5th.wav"},
    {"id": "minor_6th",   "name": "短6度 (Minor 6th)",     "ratio": (8, 5),   "semitones": 8,  "filename": "minor_6th.wav"},
    {"id": "major_6th",   "name": "長6度 (Major 6th)",     "ratio": (5, 3),   "semitones": 9,  "filename": "major_6th.wav"},
    {"id": "minor_7th",   "name": "短7度 (Minor 7th)",     "ratio": (9, 5),   "semitones": 10, "filename": "minor_7th.wav"},
    {"id": "major_7th",   "name": "長7度 (Major 7th)",     "ratio": (15, 8),  "semitones": 11, "filename": "major_7th.wav"},
    {"id": "octave",      "name": "完全8度 (Octave)",      "ratio": (2, 1),   "semitones": 12, "filename": "octave.wav"},
]

def get_interval_data() -> List[Dict]:
    return JUST_INTERVALS