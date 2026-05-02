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
    client.table("trip_requests").insert(payload).execute()
    return True


def save_chat_message(payload: dict[str, Any]) -> bool:
    client = get_supabase_client()
    if not client:
        return False
    client.table("chat_messages").insert(payload).execute()
    return True
