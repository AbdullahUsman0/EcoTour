import math
from datetime import datetime

from app.data.knowledge import CITY_COORDS, DESTINATION_TIPS


def _normalize_city(city: str) -> str:
    return city.strip().lower()


def haversine_distance_km(origin: str, destination: str) -> float:
    o = CITY_COORDS.get(_normalize_city(origin))
    d = CITY_COORDS.get(_normalize_city(destination))
    if not o or not d:
        return 0.0

    lat1, lon1 = map(math.radians, o)
    lat2, lon2 = map(math.radians, d)

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371.0 * c


def estimate_trip_cost(distance_km: float, travelers: int, demand_multiplier: float = 1.0) -> float:
    month_factor = 1.06 if datetime.utcnow().month in {6, 7, 8} else 0.96
    fuel_factor = 1.10
    base = 16500
    per_km = 160
    lodging_per_person = 4500
    return round(
        (base + distance_km * per_km + lodging_per_person * travelers)
        * month_factor
        * fuel_factor
        * demand_multiplier,
        2,
    )


def budget_message(cost: float, budget: float) -> str:
    if cost <= budget:
        return "Within budget"
    if cost <= budget * 1.2:
        return "Slightly above budget"
    return "Above budget"


def create_plan(destination: str) -> list[str]:
    tips = DESTINATION_TIPS.get(_normalize_city(destination))
    if tips:
        return tips
    return [
        "Plan flexible transport with one backup day.",
        "Confirm weather updates before finalizing mountain routes.",
        "Prioritize local guides and eco-friendly stays.",
    ]
