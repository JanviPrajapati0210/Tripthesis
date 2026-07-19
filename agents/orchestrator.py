from concurrent.futures import ThreadPoolExecutor
from agents import flights_agent, hotels_agent, itinerary_agent, budget_agent, culture_agent


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def plan_trip(user_input: dict) -> dict:
    destination    = user_input.get("destination", "Goa")
    origin         = user_input.get("origin", "Mumbai")
    duration_days  = _safe_int(user_input.get("duration_days"), 5)
    travel_dates   = user_input.get("travel_dates", "December")
    budget_level   = user_input.get("budget_level", "mid_range")
    travel_style   = user_input.get("travel_style", "couple")
    interests      = user_input.get("interests", "beaches, food, culture")
    num_travelers  = _safe_int(user_input.get("num_travelers"), 2)

    print(f"[Orchestrator] Planning trip to {destination} for {duration_days} days...")

   
    print("[Orchestrator] Calling all 5 agents in parallel...")

    with ThreadPoolExecutor(max_workers=5) as pool:
        flights_future = pool.submit(
            flights_agent.run, destination=destination, origin=origin,
            duration_days=duration_days, travel_dates=travel_dates
        )
        hotels_future = pool.submit(
            hotels_agent.run, destination=destination, duration_days=duration_days,
            budget=budget_level, travel_style=travel_style
        )
        itinerary_future = pool.submit(
            itinerary_agent.run, destination=destination, duration_days=duration_days,
            travel_style=travel_style, interests=interests
        )
        budget_future = pool.submit(
            budget_agent.run, destination=destination, duration_days=duration_days,
            budget_level=budget_level, num_travelers=num_travelers
        )
        culture_future = pool.submit(
            culture_agent.run, destination=destination, travel_style=travel_style,
            duration_days=duration_days
        )

        flights_result = flights_future.result()
        hotels_result = hotels_future.result()
        itinerary_result = itinerary_future.result()
        budget_result = budget_future.result()
        culture_result = culture_future.result()

    print("[Orchestrator] All agents done. Merging results...")

    return {
        "meta": {
            "destination": destination, "origin": origin,
            "duration_days": duration_days, "travel_dates": travel_dates,
            "travel_style": travel_style, "num_travelers": num_travelers,
            "budget_level": budget_level
        },
        "flights": flights_result,
        "hotels": hotels_result,
        "itinerary": itinerary_result,
        "budget": budget_result,
        "culture": culture_result
    }