from typing import Any

from app.config import SUPABASE_KEY, SUPABASE_URL

try:
    from supabase import Client, create_client
except Exception:  # pragma: no cover
    Client = Any  # type: ignore
    create_client = None  # type: ignore


def get_supabase_client() -> Client | None:
    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def save_trip_request(payload: dict[str, Any]) -> bool:
    client = get_supabase_client()
    if not client:
        return False
    try:
        client.table("trip_requests").insert(payload).execute()
        return True
    except Exception:
        return False


def save_chat_message(payload: dict[str, Any]) -> bool:
    client = get_supabase_client()
    if not client:
        return False
    try:
        client.table("chat_messages").insert(payload).execute()
        return True
    except Exception:
        return False


def save_itinerary(payload: dict[str, Any]) -> bool:
    client = get_supabase_client()
    if not client:
        return False
    try:
        client.table("saved_itineraries").insert(payload).execute()
        return True
    except Exception:
        return False


def list_saved_itineraries(limit: int = 10) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if not client:
        return []
    try:
        resp = (
            client.table("saved_itineraries")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


def list_trip_history(limit: int = 10) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if not client:
        return []
    try:
        resp = (
            client.table("trip_requests")
            .select("id,origin,destination,estimated_cost,budget,created_at")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


def get_trip_summary() -> dict[str, Any]:
    rows = list_trip_history(limit=50)
    if not rows:
        return {"total_trips": 0, "avg_cost": 0, "top_route": "N/A"}

    total = len(rows)
    avg_cost = round(sum(float(r.get("estimated_cost", 0)) for r in rows) / total, 2)
    route_counts: dict[str, int] = {}
    for r in rows:
        route = f"{r.get('origin', '')} -> {r.get('destination', '')}"
        route_counts[route] = route_counts.get(route, 0) + 1
    top_route = max(route_counts, key=route_counts.get) if route_counts else "N/A"
    return {"total_trips": total, "avg_cost": avg_cost, "top_route": top_route}


def delete_itinerary(itinerary_id: int) -> bool:
    client = get_supabase_client()
    if not client:
        return False
    try:
        client.table("saved_itineraries").delete().eq("id", itinerary_id).execute()
        return True
    except Exception:
        return False
