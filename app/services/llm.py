from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL


def generate_itinerary_with_llm(
    origin: str,
    destination: str,
    budget: float,
    travelers: int,
    language: str,
    weather_note: str,
    fare_note: str,
) -> list[str]:
    if not OPENAI_API_KEY:
        return []

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "You are EcoTour AI for Pakistan. Create exactly 4 concise bullets for a travel plan.\n"
        f"Origin: {origin}\nDestination: {destination}\nBudget PKR: {budget}\n"
        f"Travelers: {travelers}\nLanguage: {language}\nWeather: {weather_note}\n"
        f"Fare signal: {fare_note}\n"
        "Return only bullet lines without headings."
    )
    response = client.responses.create(model=OPENAI_MODEL, input=prompt)
    text = (response.output_text or "").strip()
    if not text:
        return []
    items = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    return items[:4]
