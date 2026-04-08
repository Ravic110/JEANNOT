from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class QuoteInput:
    client_name: str
    client_contact: str
    building_type: str
    location: str
    surface_m2: float
    floors: int
    structure_type: str
    roof_type: str
    room_count: int
    finish_level: str
    complexity: str
    notes: str = ""


@dataclass(slots=True)
class QuoteEstimate:
    total_amount: float
    applied_multipliers: dict[str, float]
    breakdown: dict[str, float]
