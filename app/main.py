from pathlib import Path

import json

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.data.knowledge import EMERGENCY_CONTACTS
from app.schemas import (
    ChatIn,
    ChatOut,
    CrisisIn,
    CrisisOut,
    ItineraryOut,
    ItinerarySaveIn,
    SpeakIn,
    TripHistoryOut,
    TripRequestIn,
    TripResponse,
)
from app.services.chat import generate_chat_reply
from app.services.crisis import crisis_response
from app.services.external_signals import get_fare_signal_note, get_live_weather_note
from app.services.llm import generate_itinerary_with_llm
from app.services.planner import budget_message, create_plan, estimate_trip_cost, haversine_distance_km
from app.services.supabase_store import (
    get_trip_summary,
    list_saved_itineraries,
    list_trip_history,
    save_chat_message,
    save_itinerary,
    save_trip_request,
)

app = FastAPI(title="EcoTour AI Pakistan")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/")
def root():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.post("/api/plan-trip", response_model=TripResponse)
def plan_trip(payload: TripRequestIn):
    distance = haversine_distance_km(payload.origin, payload.destination)
    if distance == 0.0:
        raise HTTPException(
            status_code=400,
            detail="Unknown city. Try Islamabad, Lahore, Karachi, Murree, Hunza, Gilgit, or Skardu.",
        )
    weather_note, weather_factor = get_live_weather_note(payload.destination)
    fare_note, fare_factor = get_fare_signal_note()
    estimated_cost = estimate_trip_cost(
        distance,
        payload.travelers,
        demand_multiplier=weather_factor * fare_factor,
    )
    plan = generate_itinerary_with_llm(
        payload.origin,
        payload.destination,
        payload.budget,
        payload.travelers,
        payload.language,
        weather_note,
        fare_note,
    )
    if not plan:
        plan = create_plan(payload.destination)

    save_trip_request(
        {
            "origin": payload.origin,
            "destination": payload.destination,
            "budget": payload.budget,
            "travelers": payload.travelers,
            "language": payload.language,
            "estimated_distance_km": distance,
            "estimated_cost": estimated_cost,
            "weather_note": weather_note,
            "fare_note": fare_note,
        }
    )
    return TripResponse(
        route=f"{payload.origin.title()} -> {payload.destination.title()}",
        distance_km=round(distance, 1),
        estimated_cost=estimated_cost,
        budget_fit=budget_message(estimated_cost, payload.budget),
        weather_note=weather_note,
        fare_note=fare_note,
        plan=plan,
    )


@app.post("/api/chat", response_model=ChatOut)
def chat(payload: ChatIn):
    answer = generate_chat_reply(payload.message, payload.language)
    save_chat_message(
        {
            "user_message": payload.message,
            "assistant_message": answer,
            "language": payload.language,
        }
    )
    return ChatOut(response=answer)


@app.post("/api/crisis", response_model=CrisisOut)
def crisis(payload: CrisisIn):
    severity, advice, helpline = crisis_response(payload.message, payload.language)
    return CrisisOut(severity=severity, advice=advice, helpline=helpline)


@app.get("/api/emergency")
def emergency_contacts():
    return {"contacts": EMERGENCY_CONTACTS}


@app.post("/api/itineraries")
def create_itinerary(payload: ItinerarySaveIn):
    ok = save_itinerary(
        {
            "traveler_name": payload.traveler_name,
            "route": payload.route,
            "estimated_cost": payload.estimated_cost,
            "budget_fit": payload.budget_fit,
            "plan_json": json.dumps(payload.plan),
        }
    )
    if not ok:
        raise HTTPException(
            status_code=400,
            detail="Could not save itinerary. Run supabase/saved_itineraries.sql in Supabase SQL editor.",
        )
    return {"success": True}


@app.get("/api/itineraries", response_model=list[ItineraryOut])
def get_itineraries():
    rows = list_saved_itineraries(limit=12)
    result: list[ItineraryOut] = []
    for row in rows:
        plan_raw = row.get("plan_json", "[]")
        try:
            plan = json.loads(plan_raw) if isinstance(plan_raw, str) else plan_raw
        except Exception:
            plan = []
        result.append(
            ItineraryOut(
                id=row.get("id", 0),
                traveler_name=row.get("traveler_name", "Unknown"),
                route=row.get("route", "N/A"),
                estimated_cost=float(row.get("estimated_cost", 0)),
                budget_fit=row.get("budget_fit", "N/A"),
                plan=plan or [],
                created_at=row.get("created_at", ""),
            )
        )
    return result


@app.get("/api/history/trips", response_model=list[TripHistoryOut])
def get_trip_history():
    rows = list_trip_history(limit=12)
    return [
        TripHistoryOut(
            id=r.get("id", 0),
            origin=r.get("origin", ""),
            destination=r.get("destination", ""),
            estimated_cost=float(r.get("estimated_cost", 0)),
            budget=float(r.get("budget", 0)),
            created_at=r.get("created_at", ""),
        )
        for r in rows
    ]


@app.get("/api/history/summary")
def get_history_summary():
    return get_trip_summary()


@app.post("/api/voice/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Whisper integration endpoint.
    Install openai-whisper manually for local transcription:
    pip install openai-whisper
    """
    try:
        import whisper  # type: ignore
    except Exception as exc:
        raise HTTPException(
            status_code=501,
            detail="Whisper is not installed yet. Run: pip install openai-whisper",
        ) from exc

    temp_path = BASE_DIR / "data" / file.filename
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    temp_path.write_bytes(content)

    model = whisper.load_model("base")
    result = model.transcribe(str(temp_path))
    text = result.get("text", "").strip()

    return {"text": text}


@app.post("/api/voice/speak")
def speak(payload: SpeakIn):
    """
    TTS endpoint with gTTS.
    Install: pip install gTTS
    """
    try:
        from gtts import gTTS  # type: ignore
    except Exception as exc:
        raise HTTPException(
            status_code=501,
            detail="gTTS is not installed yet. Run: pip install gTTS",
        ) from exc

    out_dir = BASE_DIR / "static" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "reply.mp3"
    tts = gTTS(payload.text)
    tts.save(str(out_file))
    return {"audio_url": "/static/generated/reply.mp3"}
