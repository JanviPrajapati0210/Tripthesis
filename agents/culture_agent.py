from groq import Groq
import json
from config import GROQ_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are a local culture and food expert for an AI travel assistant.

Your ONLY job is to share insider food, culture, and local knowledge about the destination.
Always respond in valid JSON with this exact structure:

{
  "must_try_food": [
    {
      "dish": "Fish Curry Rice",
      "description": "The soul of Goan cuisine — spicy coconut-based curry with fresh catch",
      "where_to_try": "Any local beach shack"
    }
  ],
  "cultural_tips": [
    "Dress modestly when visiting churches in Old Goa",
    "Bargain politely at local markets — it's expected"
  ],
  "local_phrases": [
    {"phrase": "Dev Borem Korum", "meaning": "God bless you / goodbye in Konkani"}
  ],
  "hidden_gems": [
    {
      "place": "Divar Island",
      "why": "Peaceful village life, colonial houses, away from tourist crowds"
    }
  ],
  "best_local_markets": ["Mapusa Friday Market", "Anjuna Flea Market"],
  "things_to_avoid": ["Avoid tap water", "Don't litter on beaches — heavy fines"]
}

Respond ONLY with JSON. No extra text before or after.
"""

def run(destination: str, travel_style: str, duration_days: int) -> dict:
    """
    Returns local culture, food tips, and hidden gems as a structured dict.
    """
    user_message = f"""
    Give me local insider knowledge for this trip:
    - Destination: {destination}
    - Travel style: {travel_style}
    - Duration: {duration_days} days
    
    Focus on authentic food, cultural tips, hidden gems, and what to avoid.
    """

    response = client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    raw = response.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Culture agent returned invalid JSON", "raw": raw}
