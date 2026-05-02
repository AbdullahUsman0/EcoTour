import requests

from app.data.knowledge import CITY_COORDS


def _normalize_city(city: str) -> str:
    return city.strip().lower()


def get_live_weather_note(destination: str) -> tuple[str, float]:
    city = _normalize_city(destination)
    coords = CITY_COORDS.get(city)
    if not coords:
        return ("Weather data unavailable for destination.", 1.0)

    lat, lon = coords
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m,precipitation",
            },
            timeout=8,
        )
        data = resp.json().get("current", {})
        temp = data.get("temperature_2m", 0)
        wind = data.get("wind_speed_10m", 0)
        precip = data.get("precipitation", 0)
        note = f"{destination.title()} now: {temp}C, wind {wind} km/h, precipitation {precip} mm."
        factor = 1.08 if wind > 35 or precip > 2 else 1.0
        return (note, factor)
    except Exception:
        return ("Live weather API unavailable, using baseline assumptions.", 1.0)


def get_fare_signal_note() -> tuple[str, float]:
    try:
        resp = requests.get(
            "https://api.exchangerate.host/latest",
            params={"base": "USD", "symbols": "PKR"},
            timeout=8,
        )
        pkr = float(resp.json()["rates"]["PKR"])
        # Travel cost pressure approximation based on FX trend bands.
        if pkr > 290:
            return (f"Currency pressure high (USD/PKR {pkr:.1f}); fares likely elevated.", 1.12)
        if pkr > 275:
            return (f"Currency pressure moderate (USD/PKR {pkr:.1f}); fares mildly elevated.", 1.05)
        return (f"Currency pressure stable (USD/PKR {pkr:.1f}); fares near baseline.", 1.0)
    except Exception:
        return ("Fare signal API unavailable, using baseline transport rates.", 1.0)
