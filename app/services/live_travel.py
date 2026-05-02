import requests

from app.data.knowledge import CITY_COORDS


def _norm(city: str) -> str:
    return city.strip().lower()


def get_route_distance_km(origin: str, destination: str) -> tuple[float, str]:
    o = CITY_COORDS.get(_norm(origin))
    d = CITY_COORDS.get(_norm(destination))
    if not o or not d:
        return (0.0, "unknown")

    try:
        lat1, lon1 = o
        lat2, lon2 = d
        url = (
            "https://router.project-osrm.org/route/v1/driving/"
            f"{lon1},{lat1};{lon2},{lat2}"
        )
        resp = requests.get(url, params={"overview": "false"}, timeout=8)
        data = resp.json()
        routes = data.get("routes") or []
        if routes:
            km = float(routes[0]["distance"]) / 1000.0
            return (km, "live_route")
    except Exception:
        pass
    return (0.0, "estimated")


def get_hotel_suggestions(destination: str, limit: int = 5) -> list[str]:
    coords = CITY_COORDS.get(_norm(destination))
    if not coords:
        return []
    lat, lon = coords
    query = f"""
    [out:json][timeout:15];
    (
      node["tourism"="hotel"](around:12000,{lat},{lon});
      node["amenity"="hotel"](around:12000,{lat},{lon});
    );
    out body {limit};
    """
    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query.encode("utf-8"),
            timeout=16,
        )
        items = resp.json().get("elements", [])
        names: list[str] = []
        for item in items:
            name = (item.get("tags") or {}).get("name")
            if name and name not in names:
                names.append(name)
            if len(names) >= limit:
                break
        return names
    except Exception:
        return []
