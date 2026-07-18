from agents.base import call_agent

SYSTEM_PROMPT = """
You are a flights planning expert for an AI travel assistant.

Your ONLY job is to suggest flight options for the user's trip.
Always respond in valid JSON with this exact structure:

{
  "suggested_routes": [
    {
      "route": "Mumbai → Goa",
      "duration": "1h 20m",
      "type": "Direct",
      "estimated_cost_inr": "3500-6000"
    }
  ],
  "best_time_to_book": "3-4 weeks in advance",
  "airlines": ["IndiGo", "Air India Express", "SpiceJet"],
  "travel_tips": ["Book early morning flights for lower prices"]
}

Keep suggestions realistic and relevant to Indian travelers.
Respond ONLY with JSON. No extra text before or after.
"""

def run(destination: str, origin: str, duration_days: int, travel_dates: str) -> dict:
    user_message = f"""
    Plan flights for this trip:
    - Origin: {origin}
    - Destination: {destination}
    - Trip duration: {duration_days} days
    - Travel dates: {travel_dates}
    
    Suggest the best flight options.
    """
    return call_agent(SYSTEM_PROMPT, user_message, label="Flights")