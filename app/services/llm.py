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
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are EcoTour AI for Pakistan. Return concise practical itinerary bullets.",
                },
                {
                    "role": "user",
                    "content": (
                        f"Origin: {origin}\nDestination: {destination}\nBudget PKR: {budget}\n"
                        f"Travelers: {travelers}\nLanguage: {language}\nWeather: {weather_note}\n"
                        f"Fare signal: {fare_note}\nReturn exactly 4 bullet lines."
                    ),
                },
            ],
            temperature=0.5,
        )
        text = (completion.choices[0].message.content or "").strip()
    except Exception:
        return []
    if not text:
        return []
    items = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    return items[:4]


def generate_chat_with_context(message: str, language: str, context: str) -> str:
    """Generate contextual chat responses with improved prompts."""
    client, model = _get_ai_client()
    if not client:
        return ""
    
    # Build a more sophisticated system prompt
    language_instruction = "Answer in Urdu with local insights" if language.lower().startswith("ur") else "Answer in English with practical tips"
    
    system_prompt = f"""You are EcoTour AI, an expert Pakistan travel assistant. {language_instruction}.

Your responses should be:
1. **Specific & Actionable** - Provide concrete recommendations, not generic advice
2. **Contextual** - Reference provided information but add original insights
3. **Varied** - Use different response formats: lists, comparisons, narratives, or structured advice
4. **Engaging** - Include relevant emojis, local insights, and cultural context
5. **Safety-First** - Always mention safety considerations when relevant
6. **Budget-Conscious** - Provide cost expectations and alternatives
7. **Bilingual-Aware** - If user mixes languages, respond helpfully

Always:
- Start with a direct answer to their question
- Include practical examples or numbers
- Suggest follow-up information they might need
- End with actionable next steps

Format your response clearly with headers and bullet points when appropriate."""

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        f"📍 **Context from Pakistan Travel Database:**\n{context}\n\n"
                        f"🌐 **Language**: {language}\n"
                        f"❓ **User Question**: {message}\n\n"
                        "Provide a helpful, specific, and engaging response. "
                        "Use the context to enhance but write original insights. "
                        "Vary your response style from previous answers."
                    ),
                },
            ],
            temperature=0.7,  # Increased for more creativity
            top_p=0.9,
            max_tokens=500,
        )
        response = (completion.choices[0].message.content or "").strip()
        return response if response else ""
    except Exception as e:
        print(f"LLM Error: {e}")
        return ""


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
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
        text = (completion.choices[0].message.content or "").strip()
    except Exception:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {}
