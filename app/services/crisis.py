from app.services.chat import bilingual


HIGH_RISK_KEYWORDS = {"accident", "fire", "flood", "earthquake", "injury", "bleeding", "attack"}
MEDIUM_RISK_KEYWORDS = {"lost", "stuck", "road closed", "landslide", "hospital"}


def classify_crisis(message: str) -> str:
    lowered = message.lower()
    if any(k in lowered for k in HIGH_RISK_KEYWORDS):
        return "high"
    if any(k in lowered for k in MEDIUM_RISK_KEYWORDS):
        return "medium"
    return "low"


def crisis_response(message: str, language: str) -> tuple[str, str, str]:
    severity = classify_crisis(message)
    if severity == "high":
        return (
            severity,
            bilingual(
                "This looks urgent. Move to a safe area immediately and call Rescue 1122 now.",
                "Yeh urgent lag raha hai. Foran safe jagah par jaen aur Rescue 1122 par call karein.",
                language,
            ),
            "1122",
        )
    if severity == "medium":
        return (
            severity,
            bilingual(
                "Stay calm, share your live location with family, and contact local authorities for route guidance.",
                "Pur-sukoon rahen, family ke sath live location share karein, aur route guidance ke liye local authorities se rabta karein.",
                language,
            ),
            "15",
        )
    return (
        severity,
        bilingual(
            "No severe risk detected. Keep emergency contacts ready and monitor weather updates.",
            "Filhal severe risk detect nahi hua. Emergency contacts ready rakhein aur weather updates dekhte rahen.",
            language,
        ),
        "1122",
    )
