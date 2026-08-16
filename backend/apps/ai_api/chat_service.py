from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
REQUEST_TIMEOUT_SECONDS = 20
MAX_HISTORY_MESSAGES = 12
MAX_MESSAGE_CHARS = 2000

SYSTEM_PROMPT = (
    "You are the MediCare AI Health Assistant, a general medical information chatbot "
    "embedded in a patient portal. Your ONLY purpose is discussing symptoms, general "
    "health information, and treatment/self-care guidance.\n\n"
    "Ground every response in the SPECIFIC details the patient actually gave you — "
    "which symptoms, how long, how severe, what makes it better or worse, their age or "
    "context if mentioned. Do not default to boilerplate. Two different symptom "
    "descriptions should read as genuinely different answers, not the same template "
    "with different nouns swapped in. Vary your sentence structure, opening line, and "
    "level of detail response to response — do not open every reply the same way, and "
    "do not force the same fixed section order every time.\n\n"
    "If the patient's description is vague or missing something clinically relevant "
    "(duration, severity, what triggers or relieves it, associated symptoms, relevant "
    "history), ask one or two focused follow-up questions before jumping to possible "
    "causes, the way a clinician would triage — don't guess from a one-line description "
    "when a quick question would let you give a much more specific answer.\n\n"
    "When you do have enough to work with, cover what's actually relevant to that "
    "case: plausible general causes (only the ones that genuinely fit what was "
    "described, not a generic list), practical self-care appropriate to the specific "
    "symptoms (not a copy-paste rest/hydration/OTC line every time — tailor it), and "
    "any red-flag/emergency signs relevant to THIS presentation specifically (chest "
    "pain, difficulty breathing, stroke signs, severe bleeding, suicidal ideation, "
    "sudden severe pain, neurological deficits, etc.) — tell the patient to seek "
    "emergency care immediately if any are present or described. Close by recommending "
    "a licensed doctor for an actual diagnosis and treatment plan when appropriate, "
    "especially for anything severe, persistent, or worsening — but don't repeat that "
    "disclaimer verbatim every single message if the conversation is continuing.\n\n"
    "Never claim to provide a diagnosis. Never prescribe specific medication names or "
    "dosages. Keep responses focused and no longer than necessary — a quick follow-up "
    "question can be one line; a fuller answer can run longer, but don't pad it.\n\n"
    "Respond only in plain prose. NEVER write programming code, code blocks, markdown "
    "code fences, scripts, or technical/software content of any kind, even if asked — "
    "you are a medical assistant, not a coding assistant. If the patient asks for "
    "anything unrelated to symptoms, health, or medical treatment (including requests "
    "for code, general chit-chat, or other tasks), politely decline and redirect them "
    "to describe a symptom or health concern instead."
)


class ChatServiceError(Exception):
    """Raised when the chatbot response could not be produced safely."""


class ChatServiceUnavailableError(ChatServiceError):
    """Raised when the upstream provider is not configured or unreachable."""


def _build_messages(message: str, history: list[dict]) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history[-MAX_HISTORY_MESSAGES:]:
        role = turn.get("role")
        content = turn.get("content", "")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content[:MAX_MESSAGE_CHARS]})
    messages.append({"role": "user", "content": message[:MAX_MESSAGE_CHARS]})
    return messages


def get_symptom_chat_reply(message: str, history: list[dict]) -> str:
    """Send the conversation to Groq and return the assistant's reply text."""

    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ChatServiceUnavailableError("Chat provider is not configured.")

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": _build_messages(message, history),
        "temperature": 0.8,
        "presence_penalty": 0.4,
        "max_tokens": 600,
    }

    try:
        response = requests.post(
            GROQ_CHAT_URL,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        logger.error("Symptom chat request to Groq failed: exception_type=%s", type(exc).__name__)
        raise ChatServiceUnavailableError("Chat provider request failed.") from exc

    if response.status_code != 200:
        logger.error("Symptom chat provider returned status_code=%s", response.status_code)
        raise ChatServiceError("Chat provider returned an error.")

    try:
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        logger.error(
            "Symptom chat provider returned an unexpected payload: exception_type=%s",
            type(exc).__name__,
        )
        raise ChatServiceError("Chat provider returned an unexpected response.") from exc

    if not isinstance(reply, str) or not reply.strip():
        raise ChatServiceError("Chat provider returned an empty response.")

    return reply.strip()
