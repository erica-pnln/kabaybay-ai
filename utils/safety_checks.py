"""Runs BEFORE any AI call. Simple keyword check; not a diagnosis."""

CRISIS_PHRASES = [
    "kill myself", "end my life", "suicide", "suicidal", "want to die",
    "don't want to live", "dont want to live", "hurt myself", "self-harm",
    "self harm", "no reason to live", "better off dead",
]

CRISIS_MESSAGE = (
    "It sounds like you may be going through something very painful. "
    "You deserve support from a real person right now. Please contact your local "
    "emergency number or a crisis hotline in your area, or reach out to a trusted "
    "friend, family member, pastor, or counselor. If you are in immediate danger, "
    "call emergency services now."
)


def is_crisis_message(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in CRISIS_PHRASES)
