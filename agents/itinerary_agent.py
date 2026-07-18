from groq import Groq
import json
from config import GROQ_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are a travel itinerary expert for an AI travel assistant.

Your ONLY job is to create a detailed day-by-day travel plan.
Always respond in valid JSON with this exact structure:

{
  "itinerary": [
    {
      "day": 1,
      "title": "Arrival & North Goa Exploration",
      "morning": "Arrive, check in, freshen up. Visit Baga Beach.",
      "afternoon": "Explore Calangute market. Try local Goan thali for lunch.",
      "evening": "Sunset at Anjuna Beach. Dinner at a beach shack.",
      "places": ["Baga Beach", "Calangute Market", "Anjuna Beach"],
      "estimated_local_spend_inr": 1200
    }
  ],
  "general_tips": ["Rent a scooter for easy local travel"],
  "must_visit": ["Dudhsagar Falls", "Old Goa Churches"]
}

Create one entry per day. Be specific with place names and activities.
Respond ONLY with JSON. No extra text before or after.
"""

def run(destination: str, duration_days: int, travel_style: str, interests: str) -> dict:
    """
    Returns a day-by-day itinerary as a structured dict.
    
    interests: e.g. "beaches, food, history, adventure"
    """
    user_message = f"""
    Create a {duration_days}-day itinerary for this trip:
    - Destination: {destination}
    - Travel style: {travel_style}
    - Interests: {interests}
    
    Make it detailed and practical, day by day.
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
        return {"error": "Itinerary agent returned invalid JSON", "raw": raw}
