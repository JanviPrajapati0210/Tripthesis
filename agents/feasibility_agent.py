"""
feasibility_agent.py

--- CONCEPT: Agent-reviews-agent ---
Every other agent in this system generates content in isolation — the
itinerary agent has no idea if the places it lists are actually near
each other, or if it's cramming too much into one day.

This agent's ONLY job is to read the itinerary agent's output and
critique it: flag days that are geographically scattered, overpacked,
or logically inconsistent. This is what makes the system "multi-agent"
in a meaningful sense — not just 5 agents that never see each other's
output, but one agent whose entire job is to reason about another
agent's result.
"""

from agents.base import call_agent
import json

SYSTEM_PROMPT = """
You are a travel-feasibility reviewer for an AI travel assistant.

You will be given a day-by-day itinerary (as JSON) that another agent
already generated. Your ONLY job is to critically review it — you do
NOT rewrite the itinerary, you only assess it.

Check for:
- Geographic feasibility: are the places listed for a single day
  realistically close enough to visit in one day, given the destination?
- Pacing: is any day overpacked (too many activities) or too sparse for
  the stated travel style?
- Logical consistency: do the morning/afternoon/evening activities make
  sense in sequence (e.g. not scheduling a sunset activity in the
  morning slot)?
- Realistic time budget: does the day's activities fit in a reasonable
  waking day (roughly 8am-10pm) without being rushed?

Always respond in valid JSON with this exact structure:

{
  "overall_feasibility": "high" | "medium" | "low",
  "summary": "One or two sentence overall verdict.",
  "day_reviews": [
    {
      "day": 1,
      "status": "ok" | "minor_issue" | "flagged",
      "note": "Short explanation. If status is 'ok', a brief confirmation is enough."
    }
  ],
  "suggestions": ["Actionable suggestion 1", "Actionable suggestion 2"]
}

Be honest and specific — if everything looks fine, say so plainly rather
than inventing issues. Respond ONLY with JSON. No extra text before or after.
"""


def run(destination: str, itinerary_result: dict, travel_style: str) -> dict:
    """
    Reviews an already-generated itinerary for feasibility issues.

    itinerary_result: the dict returned by itinerary_agent.run() —
    must contain an "itinerary" list to be reviewable.
    """
    if not itinerary_result or "error" in itinerary_result or not itinerary_result.get("itinerary"):
        return {
            "overall_feasibility": "unknown",
            "summary": "No itinerary was available to review.",
            "day_reviews": [],
            "suggestions": []
        }

    user_message = f"""
    Review this {destination} itinerary for a {travel_style} trip:

    {json.dumps(itinerary_result, indent=2)}

    Assess feasibility day by day.
    """

    return call_agent(SYSTEM_PROMPT, user_message, label="Feasibility")