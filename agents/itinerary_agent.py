from agents.base import call_agent
import json

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

# --- CONCEPT: A second, narrower prompt for targeted edits ---
# The original SYSTEM_PROMPT is for generating a plan from nothing.
# Refining is a different task: the model already has a full itinerary
# and should change ONLY what the feedback asks for, leaving everything
# else as close to untouched as possible.
REFINE_SYSTEM_PROMPT = """
You are a travel itinerary editor for an AI travel assistant.

You will be given an EXISTING day-by-day itinerary (as JSON) and a
piece of user feedback describing what they want changed.

Your job is to return an UPDATED version of the itinerary that
addresses the feedback, while keeping everything the feedback didn't
ask about as close to the original as possible. Do not regenerate days
or details that aren't affected by the feedback.

Respond in the exact same JSON structure as the original itinerary:

{
  "itinerary": [
    {
      "day": 1,
      "title": "...",
      "morning": "...",
      "afternoon": "...",
      "evening": "...",
      "places": ["..."],
      "estimated_local_spend_inr": 1200
    }
  ],
  "general_tips": ["..."],
  "must_visit": ["..."]
}

Respond ONLY with the full updated JSON. No extra text before or after.
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

    return call_agent(SYSTEM_PROMPT, user_message, label="Itinerary")


def refine(destination: str, duration_days: int, travel_style: str,
           current_itinerary: dict, feedback: str) -> dict:
    """
    Updates an EXISTING itinerary based on free-text user feedback,
    instead of generating a new one from scratch. This is what powers
    "chat-based regeneration" — only this one agent re-runs when the
    user asks for a tweak, not the whole 5-6 agent pipeline.
    """
    user_message = f"""
    Here is the current itinerary for a {duration_days}-day trip to
    {destination} ({travel_style} travel style):

    {json.dumps(current_itinerary, indent=2)}

    The user's requested change:
    "{feedback}"

    Update the itinerary to address this feedback. Keep any days or
    details that aren't related to the feedback unchanged. Return the
    FULL updated itinerary using the same JSON schema.
    """

    return call_agent(REFINE_SYSTEM_PROMPT, user_message, label="Itinerary Refinement")