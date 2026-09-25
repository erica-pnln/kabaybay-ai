"""Secure AI reflection generation using only dataset-backed Scripture."""
import json
import os
import re
from dataclasses import dataclass

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

PRAYER_INTRO = "In the name of the Father, and of the Son, and of the Holy Spirit. Amen."
PRAYER_ENDING = "In Jesus’ name, I pray. Amen."
LANGUAGE_NAMES = {
    "🇬🇧 English": "English",
    "🇵🇭 Bisaya (Cebuano)": "Bisaya (Cebuano)",
    "🇵🇭 Tagalog": "Tagalog",
}
PRAYER_INTROS = {
    "English": PRAYER_INTRO,
    "Bisaya (Cebuano)": "Sa ngalan sa Amahan, ug sa Anak, ug sa Espiritu Santo. Amen.",
    "Tagalog": "Sa ngalan ng Ama, at ng Anak, at ng Espiritu Santo. Amen.",
}
PRAYER_ENDINGS = {
    "English": PRAYER_ENDING,
    "Bisaya (Cebuano)": "Sa ngalan ni Jesus, nagaampo ako. Amen.",
    "Tagalog": "Sa ngalan ni Jesus, ako ay nananalangin. Amen.",
}
DEFAULT_MODEL = "openai/gpt-oss-20b"

load_dotenv()


@dataclass
class ReflectionResult:
    """A generated result or a user-safe error message."""

    ok: bool
    message: str
    explanation: str = ""
    reflection: str = ""
    prayer: str = ""


def _setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def _api_configuration() -> tuple[str, str]:
    api_key = (
        _setting("AI_API_KEY")
        or _setting("GROQ_API_KEY")
        or _setting("FAITHGUIDE_AI_API_KEY")
        or _setting("OPENAI_API_KEY")
    )
    model = (
        _setting("AI_MODEL")
        or _setting("GROQ_MODEL")
        or _setting("FAITHGUIDE_AI_MODEL")
        or _setting("OPENAI_MODEL")
        or DEFAULT_MODEL
    )
    return api_key, model


def format_scripture_passage(passage_df: pd.DataFrame) -> str:
    """Format only rows supplied by the verified Bible dataframe."""
    rows = passage_df.sort_values("verse")
    return "\n".join(
        f"{row.reference}: {row.text}" for row in rows.itertuples()
    )


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def _limit_sentences(text: str, maximum: int) -> str:
    return " ".join(_sentences(text)[:maximum])


def _build_prompt(
    emotion: str, message: str, reference: str, passage: str, language: str
) -> str:
    language_name = LANGUAGE_NAMES.get(language, "English")
    return f"""Create a gentle Christian reflection based only on the supplied Scripture passage.

User emotion: {emotion}
User message: {message}
Selected passage reference: {reference}
Response language: {language_name}

Verified Scripture from the application's dataset:
---
{passage}
---

Return valid JSON with exactly these string fields:
- explanation: a short explanation of the supplied passage; do not add or paraphrase it as a quotation.
- reflection: an empathetic Bible reflection of no more than 5 sentences.
- prayer_body: exactly 3 or 4 sentences, excluding the required introduction and ending.

Write explanation, reflection, and prayer_body naturally in {language_name}. Keep the language easy to understand.
Do not translate, rewrite, or alter the supplied Scripture passage; it must remain the original dataset text.

Do not claim to be God, speak as God, or present the response as a direct message from God.
Do not invent Bible verses, references, quotations, or facts. If referring to Scripture, use only the supplied passage.
Do not include the prayer introduction or ending in prayer_body; the application will add them exactly.
"""


def generate_reflection(
    emotion: str,
    message: str,
    passage_df: pd.DataFrame,
    reference: str,
    language: str = "🇬🇧 English",
) -> ReflectionResult:
    """Generate reflection content without exposing credentials or inventing Scripture."""
    if passage_df.empty:
        return ReflectionResult(False, "A verified Scripture passage is required before requesting a reflection.")

    language_name = LANGUAGE_NAMES.get(language, "English")
    api_key, model = _api_configuration()
    if not api_key:
        return ReflectionResult(
            False,
            "AI reflection is not configured yet. Add GROQ_API_KEY or AI_API_KEY to your environment or Streamlit Secrets.",
        )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=0.4,
            max_completion_tokens=2048,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a careful Christian reflection assistant. Follow the requested JSON contract.",
                },
                {"role": "user", "content": _build_prompt(
                    emotion, message, reference, format_scripture_passage(passage_df), language
                )},
            ],
        )
        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
        explanation = str(result.get("explanation", "")).strip()
        reflection = _limit_sentences(str(result.get("reflection", "")), 5)
        prayer_body = str(result.get("prayer_body", "")).strip()
        prayer_sentences = _sentences(prayer_body)
        if not explanation or not reflection or len(prayer_sentences) not in {3, 4}:
            return ReflectionResult(False, "The AI returned an incomplete reflection. Please try again.")
        prayer = (
            f"{PRAYER_INTROS[language_name]}\n\n{prayer_body}\n\n"
            f"{PRAYER_ENDINGS[language_name]}"
        )
        return ReflectionResult(True, "Reflection generated.", explanation, reflection, prayer)
    except Exception:
        return ReflectionResult(
            False,
            "The reflection service is temporarily unavailable. Your message was not saved or displayed as Scripture.",
        )
