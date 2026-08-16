from flask import Flask, render_template, request, Response, session, jsonify
from agents import flights_agent, hotels_agent, itinerary_agent, budget_agent, culture_agent
from agents.orchestrator import plan_trip
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents import flights_agent, hotels_agent, itinerary_agent, budget_agent, culture_agent, feasibility_agent
import json
import os
import urllib.request
import urllib.parse
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def safe_int(value, default):
    """
    --- CONCEPT: Defensive parsing ---
    request.form.get() always returns a string (or None). Calling
    int() directly on it crashes the whole request with a 500 error
    if the field is empty, missing, or someone types non-numeric text.
    This helper falls back to a sane default instead of crashing.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default



app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is not set. Add it to your .env file "
        "(generate one with: python -c \"import secrets; print(secrets.token_hex(32))\")"
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/plan", methods=["POST"])
def plan():
    """Original non-streaming fallback route."""
    user_input = {
        "destination":   request.form.get("destination"),
        "origin":        request.form.get("origin"),
        "duration_days": request.form.get("duration_days"),
        "travel_dates":  request.form.get("travel_dates"),
        "budget_level":  request.form.get("budget_level"),
        "travel_style":  request.form.get("travel_style"),
        "interests":     request.form.get("interests"),
        "num_travelers": request.form.get("num_travelers"),
    }
    travel_plan = plan_trip(user_input)
    return render_template("result.html", plan=travel_plan)


@app.route("/plan-stream", methods=["POST"])
def plan_stream():
    """
    SSE entry point.
    Saves form data to session, renders stream.html immediately.
    stream.html then opens /stream-events to receive agent results live.
    """
    session["user_input"] = {
        "destination":   request.form.get("destination"),
        "origin":        request.form.get("origin"),
        "duration_days": request.form.get("duration_days"),
        "travel_dates":  request.form.get("travel_dates"),
        "budget_level":  request.form.get("budget_level"),
        "travel_style":  request.form.get("travel_style"),
        "interests":     request.form.get("interests"),
        "num_travelers": request.form.get("num_travelers"),
    }
    return render_template("stream.html", user_input=session["user_input"])


@app.route("/stream-events")
def stream_events():
    """
    SSE generator — runs all 5 agents concurrently via a thread pool,
    yielding each result to the browser the moment it finishes.
    """
    user_input    = session.get("user_input", {})
    destination   = user_input.get("destination", "Goa")
    origin        = user_input.get("origin", "Mumbai")
    duration_days = safe_int(user_input.get("duration_days"), 5)
    travel_dates  = user_input.get("travel_dates", "December")
    budget_level  = user_input.get("budget_level", "mid_range")
    travel_style  = user_input.get("travel_style", "couple")
    interests     = user_input.get("interests", "beaches, food")
    num_travelers = safe_int(user_input.get("num_travelers"), 2)

    def generate():
        def event(agent_name, data):
            payload = json.dumps({"agent": agent_name, "data": data})
            return f"data: {payload}\n\n"

        labels = {
            "flights":   "✈️ Flights agent working...",
            "hotels":    "🏨 Hotels agent working...",
            "itinerary": "🗓️ Itinerary agent building your days...",
            "budget":    "💰 Budget agent calculating costs...",
            "culture":   "🍛 Culture agent finding local tips...",
        }
        for msg in labels.values():
            yield event("status", {"message": msg})

        itinerary_result = None

        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {
                pool.submit(flights_agent.run, destination, origin, duration_days, travel_dates): "flights",
                pool.submit(hotels_agent.run, destination, duration_days, budget_level, travel_style): "hotels",
                pool.submit(itinerary_agent.run, destination, duration_days, travel_style, interests): "itinerary",
                pool.submit(budget_agent.run, destination, duration_days, budget_level, num_travelers): "budget",
                pool.submit(culture_agent.run, destination, travel_style, duration_days): "culture",
            }

            
            feasibility_future = None

            for future in as_completed(futures):
                agent_name = futures[future]
                result = future.result()
                yield event(agent_name, result)

                if agent_name == "itinerary":
                    itinerary_result = result
                    yield event("status", {"message": "🔍 Feasibility agent reviewing your itinerary..."})
                    feasibility_future = pool.submit(
                        feasibility_agent.run, destination, itinerary_result, travel_style
                    )

            if feasibility_future is not None:
                feasibility_result = feasibility_future.result()
                yield event("feasibility", feasibility_result)

        yield event("status", {"message": "🗺️ Mapping your itinerary places..."})
        map_pins = geocode_places(itinerary_result or {}, destination)
        yield event("map", {"pins": map_pins})

        meta = {
            "destination": destination, "origin": origin,
            "duration_days": duration_days, "travel_dates": travel_dates,
            "travel_style": travel_style, "num_travelers": num_travelers,
            "budget_level": budget_level
        }
        yield event("done", {"meta": meta})

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


def geocode_places(itinerary_result: dict, destination: str) -> list:
    """
    --- CONCEPT: Geocoding ---
    Geocoding = converting a place name (string) into coordinates (lat, lon).

    We use Nominatim — OpenStreetMap's free geocoding API.
    No API key needed. Rate limit: 1 request per second (we respect this).

    For each day in the itinerary, we take the places list and
    geocode each one, appending the destination name for accuracy
    (e.g. "Baga Beach, Goa" instead of just "Baga Beach").

    Returns a list of pin objects:
    [{ "name": "Baga Beach", "lat": 15.55, "lon": 73.75, "day": 1 }, ...]
    """
    pins = []
    days = itinerary_result.get("itinerary", [])

    
    DAY_COLORS = ["#7c6aff", "#1D9E75", "#f59e0b", "#ef4444",
                  "#06b6d4", "#ec4899", "#84cc16", "#4f16f9"]

    for day in days:
        day_num = day.get("day", 1)
        places  = day.get("places", [])
        color   = DAY_COLORS[(day_num - 1) % len(DAY_COLORS)]

        for place in places:
            
            query = f"{place}, {destination}"
            print(f"Searching: {query}")
            encoded = urllib.parse.quote(query)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"

            try:
                
                req = urllib.request.Request(url, headers={
                    "User-Agent": "AI-Travel-Planner/1.0"
                })
                with urllib.request.urlopen(req, timeout=5) as resp:
                    results = json.loads(resp.read().decode())
                    if results:
                        print(f"FOUND: {place}")
                        print(f"LAT: {results[0]['lat']}")
                        print(f"LON: {results[0]['lon']}")
                        print("-" * 50)

                        pins.append({
                            "name":  place,
                            "lat":   float(results[0]["lat"]),
                            "lon":   float(results[0]["lon"]),
                            "day":   day_num,
                            "color": color
                        })
            except Exception:
            
                pass

            
            time.sleep(1.1)

    return pins



@app.route("/save-plan", methods=["POST"])
def save_plan():
    """
    --- CONCEPT: Saving the plan for PDF export ---

    The travel plan is built piece by piece during streaming.
    JavaScript collects each agent's result as it arrives,
    then POSTs the full merged plan here when streaming is done.
    We store it in the session so /download-pdf can access it.

    Why not store it during streaming?
    The SSE generator runs in its own thread. Writing to session
    from inside a generator is unreliable. It's cleaner to let
    the frontend assemble the full plan and send it back.
    """
    data = request.get_json()
    session["travel_plan"] = data
    return jsonify({"status": "saved"})

@app.route("/refine-itinerary", methods=["POST"])
def refine_itinerary():
    """
    --- CONCEPT: Targeted agent invocation ---
    Instead of regenerating the entire 6-agent plan when the user wants
    a small change, this route re-runs ONLY the itinerary agent (with
    their feedback as extra context), then re-checks feasibility on the
    updated itinerary and re-geocodes the map. Flights, hotels, budget,
    and culture are left completely untouched.
    """
    data = request.get_json(silent=True) or {}

    destination        = data.get("destination", "Goa")
    duration_days      = safe_int(data.get("duration_days"), 5)
    travel_style        = data.get("travel_style", "couple")
    current_itinerary   = data.get("itinerary", {})
    feedback            = (data.get("feedback") or "").strip()

    if not feedback:
        return jsonify({"error": "Tell me what you'd like to change about the itinerary."}), 400

    if not current_itinerary or not current_itinerary.get("itinerary"):
        return jsonify({"error": "No existing itinerary to refine yet."}), 400

    updated_itinerary = itinerary_agent.refine(
        destination=destination,
        duration_days=duration_days,
        travel_style=travel_style,
        current_itinerary=current_itinerary,
        feedback=feedback
    )

    if "error" in updated_itinerary:
        return jsonify({"error": updated_itinerary["error"]}), 502

    feasibility_result = feasibility_agent.run(destination, updated_itinerary, travel_style)
    map_pins = geocode_places(updated_itinerary, destination)

    return jsonify({
        "itinerary": updated_itinerary,
        "feasibility": feasibility_result,
        "map_pins": map_pins
    })

from agents.pdf_generator import generate_pdf
from flask import send_file

@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    """
    --- CONCEPT: In-memory PDF download ---

    Receives the full travel_plan as JSON from the browser (posted via
    a hidden form after all agents finish), generates the PDF in memory
    using ReportLab, and sends it as a file download.

    No file is written to disk — generate_pdf() returns bytes,
    we wrap them in BytesIO, and Flask streams them to the browser.

    send_file() sets the correct Content-Type and Content-Disposition
    headers so the browser treats it as a download, not a page load.
    """
    from io import BytesIO

    
    plan_json = request.form.get("plan_data", "{}")
    travel_plan = json.loads(plan_json)

    destination = travel_plan.get("meta", {}).get("destination", "trip")
    filename = f"travel-plan-{destination.lower().replace(' ', '-')}.pdf"

    pdf_bytes = generate_pdf(travel_plan)
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, threaded=True)