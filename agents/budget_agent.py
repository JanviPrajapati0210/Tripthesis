from groq import Groq
import json
from config import GROQ_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are a travel budget estimation expert for an AI travel assistant.

Your ONLY job is to calculate a realistic trip budget breakdown.
Always respond in valid JSON with this exact structure:

{
  "currency": "INR",
  "duration_days": 5,
  "budget_breakdown": {
    "flights": {"min": 3500, "max": 7000, "note": "Round trip economy"},
    "accommodation": {"min": 8000, "max": 25000, "note": "For full stay"},
    "food": {"min": 3000, "max": 8000, "note": "₹600-1600/day"},
    "local_transport": {"min": 1500, "max": 3000, "note": "Scooter or taxi"},
    "activities": {"min": 2000, "max": 5000, "note": "Entry fees, water sports"},
    "shopping_misc": {"min": 1000, "max": 5000, "note": "Souvenirs, toiletries"}
  },
  "total": {
    "budget_trip": 19000,
    "comfortable_trip": 35000,
    "luxury_trip": 65000
  },
  "money_saving_tips": ["Eat at local shacks instead of tourist restaurants"]
}

Respond ONLY with JSON. No extra text before or after.
"""

def run(destination: str, duration_days: int, budget_level: str, num_travelers: int) -> dict:
    """
    Returns a detailed budget breakdown as a structured dict.
    """
    user_message = f"""
    Estimate the budget for this trip:
    - Destination: {destination}
    - Duration: {duration_days} days
    - Budget level preference: {budget_level}
    - Number of travelers: {num_travelers}
    
    Give a realistic, itemized cost breakdown in INR.
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
        return {"error": "Budget agent returned invalid JSON", "raw": raw}
