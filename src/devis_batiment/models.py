from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MaterialLine:
    name: str
    unit: str
    quantity: float
    unit_price: float
    line_total: float


@dataclass(slots=True)
class QuoteInput:
    client_name: str
    client_contact: str
    project_name: str
    project_type: str
    location: str
    surface_m2: float
    length_m: float
    width_m: float
    height_m: float
    thickness_m: float
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
    materials: list[MaterialLine]
    volume_m3: float
