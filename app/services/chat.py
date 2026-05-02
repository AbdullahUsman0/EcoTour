from app.data.knowledge import DESTINATION_TIPS


def bilingual(text_en: str, text_ur: str, language: str) -> str:
    if language.lower().startswith("ur"):
        return text_ur
    return text_en


def generate_chat_reply(message: str, language: str) -> str:
    lowered = message.lower()
    for destination, tips in DESTINATION_TIPS.items():
        if destination in lowered:
            joined = " ".join(tips)
            return bilingual(
                f"For {destination.title()}, here is a quick guide: {joined}",
                f"{destination.title()} ke liye quick guide: {joined}",
                language,
            )

    if "budget" in lowered or "cost" in lowered:
        return bilingual(
            "Share your origin, destination, and budget. I will estimate distance and trip cost for Pakistan routes.",
            "Apni origin, destination aur budget share karein. Main aap ke liye distance aur estimated cost nikal dunga.",
            language,
        )
    if "emergency" in lowered or "help" in lowered:
        return bilingual(
            "Use the Crisis Help tab for safety advice and one-tap emergency call links.",
            "Safety advice aur one-tap emergency call links ke liye Crisis Help tab use karein.",
            language,
        )

    return bilingual(
        "I can plan Pakistan tours, estimate cost, suggest places, and help in emergencies. Ask me in English or Urdu.",
        "Main Pakistan tours plan kar sakta hoon, cost estimate kar sakta hoon, places suggest kar sakta hoon aur emergency help de sakta hoon. Aap English ya Urdu mein pooch sakte hain.",
        language,
    )


def fallback_rag_style_reply(message: str, context: str, language: str) -> str:
    if language.lower().startswith("ur"):
        return (
            "Aap ke sawal ke liye relevant maloomat mil gayi hai:\n"
            f"{context[:700]}\n\n"
            "Agar aap exact route, budget, aur days batayen to main better travel plan de sakta hoon."
        )
    return (
        "I found relevant travel context for your question:\n"
        f"{context[:700]}\n\n"
        "Share your exact route, budget, and number of days for a more precise plan."
    )
