from groq import Groq
import json
from config import GROQ_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are a hotels and accommodation expert for an AI travel assistant.

Your ONLY job is to recommend where to stay based on budget and travel style.
Always respond in valid JSON with this exact structure:

{
  "recommended_areas": [
    {
      "area": "Calangute",
      "why": "Best for nightlife and beach access",
      "hotel_type": "Beach resort"
    }
  ],
  "budget_breakdown": {
    "budget": "₹1500-2500/night — guesthouses, hostels",
    "mid_range": "₹3000-6000/night — 3-star hotels",
    "luxury": "₹8000+/night — 5-star resorts"
  },
  "top_picks": [
    {
      "name": "Example Hotel Name",
      "area": "North Goa",
      "tier": "mid_range",
      "highlights": ["Pool", "Beach view", "Breakfast included"]
    }
  ],
  "booking_tips": ["Book 4-6 weeks ahead for peak season"]
}

Respond ONLY with JSON. No extra text before or after.
"""

def run(destination: str, duration_days: int, budget: str, travel_style: str) -> dict:
    """
    Returns hotel recommendations as a structured dict.
    
    budget: "budget" | "mid_range" | "luxury"
    travel_style: e.g. "solo backpacker", "couple", "family"
    """
    user_message = f"""
    Find accommodation for this trip:
    - Destination: {destination}
    - Duration: {duration_days} nights
    - Budget level: {budget}
    - Travel style: {travel_style}
    
    Recommend the best areas and hotels.
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
        return {"error": "Hotels agent returned invalid JSON", "raw": raw}
