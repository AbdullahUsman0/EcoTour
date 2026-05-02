import json

from openai import OpenAI

from app.config import (
    AI_PROVIDER,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)


def _get_ai_client() -> tuple[OpenAI | None, str]:
    provider = AI_PROVIDER.lower()
    if provider == "groq" and GROQ_API_KEY:
        return (OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1"), GROQ_MODEL)
    if provider == "openrouter" and OPENROUTER_API_KEY:
        return (
            OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1"),
            OPENROUTER_MODEL,
        )
    if OPENAI_API_KEY:
        return (OpenAI(api_key=OPENAI_API_KEY), OPENAI_MODEL)
    return (None, "")


def generate_itinerary_with_llm(
    origin: str,
    destination: str,
    budget: float,
    travelers: int,
    language: str,
    weather_note: str,
    fare_note: str,
) -> list[str]:
    client, model = _get_ai_client()
    if not client:
        return []
    prompt = (
        "You are EcoTour AI for Pakistan. Create exactly 4 concise bullets for a travel plan.\n"
        f"Origin: {origin}\nDestination: {destination}\nBudget PKR: {budget}\n"
        f"Travelers: {travelers}\nLanguage: {language}\nWeather: {weather_note}\n"
        f"Fare signal: {fare_note}\n"
        "Return only bullet lines without headings."
    )
    response = client.responses.create(model=model, input=prompt)
    text = (response.output_text or "").strip()
    if not text:
        return []
    items = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    return items[:4]


def generate_chat_with_context(message: str, language: str, context: str) -> str:
    client, model = _get_ai_client()
    if not client:
        return ""
    prompt = (
        "You are EcoTour AI, an expert Pakistan travel assistant.\n"
        "Answer the user using the provided context first. If context is incomplete, still provide practical guidance.\n"
        "Keep answer actionable and concise with bullet points where useful.\n"
        f"Language preference: {language}\n\n"
        f"Context:\n{context}\n\n"
        f"User question:\n{message}\n"
    )
    response = client.responses.create(model=model, input=prompt)
    return (response.output_text or "").strip()


def generate_trip_options_with_llm(
    origin: str,
    destination: str,
    budget: float,
    travelers: int,
    preferences: dict[str, str],
    weather_note: str,
    fare_note: str,
) -> dict:
    client, model = _get_ai_client()
    if not client:
        return {}
    prompt = (
        "You are a travel planning AI for Pakistan. Return valid JSON only.\n"
        "Generate three options: budget, balanced, premium.\n"
        "Each option must include title, estimated_cost, highlights (3 bullets).\n"
        "Also include do_now (3 items) and avoid_now (3 items).\n"
        f"Origin: {origin}\nDestination: {destination}\nBudget: {budget}\nTravelers: {travelers}\n"
        f"Preferences: {preferences}\nWeather: {weather_note}\nFare: {fare_note}\n"
        'Output JSON schema: {"options":[{"title":"","estimated_cost":0,"highlights":["","",""]}],"do_now":["","",""],"avoid_now":["","",""]}'
    )
    response = client.responses.create(model=model, input=prompt)
    text = (response.output_text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        return {}
