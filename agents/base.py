"""
base.py

--- CONCEPT: Shared agent infrastructure ---
Every sub-agent (flights, hotels, itinerary, budget, culture) was doing the
exact same three things:
  1. Create a Groq client
  2. Call chat.completions.create() with its own system prompt
  3. Parse the JSON response, with a fallback if parsing fails

That's duplicated across 5 files. This module centralizes it so:
  - There's ONE Groq client (created once, reused by all agents)
  - There's ONE place that handles API failures (network errors, rate
    limits, timeouts) — previously these were NOT caught anywhere, so a
    Groq hiccup would crash the whole SSE stream mid-request.
  - There's ONE place that handles malformed JSON from the model
"""

from groq import Groq
import json
from config import GROQ_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS


client = Groq(api_key=GROQ_API_KEY)


def call_agent(system_prompt: str, user_message: str, label: str, max_tokens: int = None) -> dict:
    """
    Calls the Groq API with a given system prompt + user message,
    and returns a parsed dict.

    label: human-readable agent name, used only in error messages.
    max_tokens: optional override of the default MAX_TOKENS from config.
                Useful for agents (like itinerary generation/refinement)
                that produce larger structured output than the rest.

    Returns either the parsed JSON dict, or {"error": ...} if the call
    failed or the model didn't return valid JSON.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=max_tokens or MAX_TOKENS,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
    except Exception as e:
        return {
            "error": f"{label} agent could not reach the AI service",
            "details": str(e),
        }

    raw = response.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": f"{label} agent returned invalid JSON", "raw": raw}