from __future__ import annotations

TIER_ORDER = ["centrum", "vesten_of_rand"]
TIER_COLORS = {"centrum": "#2563EB", "vesten_of_rand": "#16A34A"}

PARKING_ORDER = [
    "P Grote Markt",
    "P Hoogstraat",
    "P Kathedraal",
    "P Lamot",
    "P Veemarkt",
    "P Bruul",
    "P Komet",
    "P Maarten",
    "P Tinel",
    "P Keerdok",
]

PARKING_TIER_MAP = {
    "P Grote Markt": "centrum",
    "P Hoogstraat": "centrum",
    "P Kathedraal": "centrum",
    "P Lamot": "centrum",
    "P Veemarkt": "centrum",
    "P Bruul": "vesten_of_rand",
    "P Komet": "vesten_of_rand",
    "P Maarten": "vesten_of_rand",
    "P Tinel": "vesten_of_rand",
    "P Keerdok": "vesten_of_rand",
}

SEASON_ORDER = ["winter", "lente", "zomer", "herfst"]
SEASON_COLORS = {
    "winter": "#3B82F6",
    "lente": "#22C55E",
    "zomer": "#F59E0B",
    "herfst": "#EF4444",
}

DAY_TYPE_3_ORDER = ["weekday", "saturday", "sunday_holiday"]
DAY_TYPE_3_LABELS = {
    "weekday": "Weekdag (ma-vr)",
    "saturday": "Zaterdag",
    "sunday_holiday": "Zondag / Feestdag",
}
