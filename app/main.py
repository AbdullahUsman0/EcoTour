from pathlib import Path

import json
import os
import shutil

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
from app.services.live_travel import get_hotel_suggestions, get_route_distance_km
from app.services.llm import (
    generate_chat_with_context,
    generate_itinerary_with_llm,
    generate_trip_options_with_llm,
)
from app.services.planner import budget_message, create_plan, estimate_trip_cost, haversine_distance_km
from app.services.rag import retrieve_context
from app.services.supabase_store import (
    delete_itinerary,
    get_trip_summary,
    list_saved_itineraries,
    list_trip_history,
    save_chat_message,
    save_itinerary,
    save_trip_request,
)
from app.services.chat import fallback_rag_style_reply

app = FastAPI(title="EcoTour AI Pakistan")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/")
def root():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.post("/api/plan-trip", response_model=TripResponse)
def plan_trip(payload: TripRequestIn):
    live_distance, distance_source = get_route_distance_km(payload.origin, payload.destination)
    distance = live_distance if live_distance > 0 else haversine_distance_km(payload.origin, payload.destination)
    if distance_source == "estimated":
        distance_source = "estimated_haversine"
    if distance == 0.0:
        raise HTTPException(
            status_code=400,
            detail="Unknown city. Try Islamabad, Lahore, Karachi, Murree, Hunza, Gilgit, or Skardu.",
        )
    weather_note, weather_factor = get_live_weather_note(payload.destination)
    fare_note, fare_factor = get_fare_signal_note()
    hotel_suggestions = get_hotel_suggestions(payload.destination, limit=5)
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
    ai_options = generate_trip_options_with_llm(
        payload.origin,
        payload.destination,
        payload.budget,
        payload.travelers,
        {
            "hotel_tier": payload.hotel_tier,
            "transport_mode": payload.transport_mode,
            "activity_pace": payload.activity_pace,
            "food_style": payload.food_style,
        },
        weather_note,
        fare_note,
    )
    options = ai_options.get("options", []) if isinstance(ai_options, dict) else []
    do_now = ai_options.get("do_now", []) if isinstance(ai_options, dict) else []
    avoid_now = ai_options.get("avoid_now", []) if isinstance(ai_options, dict) else []
    if not options:
        options = [
            {
                "title": "Budget Explorer",
                "estimated_cost": round(estimated_cost * 0.85, 2),
                "highlights": ["Guesthouse stays", "Shared transport", "Public food spots"],
            },
            {
                "title": "Balanced Comfort",
                "estimated_cost": round(estimated_cost, 2),
                "highlights": ["3-star hotels", "Mixed transport", "Top attractions + local food"],
            },
            {
                "title": "Premium Experience",
                "estimated_cost": round(estimated_cost * 1.35, 2),
                "highlights": ["Premium hotels", "Private transfers", "Guided curated activities"],
            },
        ]
    if not do_now:
        do_now = ["Lock hotels early", "Keep weather backup day", "Carry emergency cash and IDs"]
    if not avoid_now:
        avoid_now = ["Do not overpack schedule", "Avoid night mountain driving", "Avoid single-use plastics"]

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
        distance_source=distance_source,
        estimated_cost=estimated_cost,
        budget_fit=budget_message(estimated_cost, payload.budget),
        weather_note=weather_note,
        fare_note=fare_note,
        hotel_suggestions=hotel_suggestions,
        plan=plan,
        options=options,
        do_now=do_now,
        avoid_now=avoid_now,
    )


@app.post("/api/chat", response_model=ChatOut)
def chat(payload: ChatIn):
    context, sources = retrieve_context(payload.message)
    composed_message = payload.message
    if payload.screen_context:
        composed_message = f"{payload.message}\n\nScreen context:\n{payload.screen_context}"
    answer = generate_chat_with_context(composed_message, payload.language, context)
    if not answer:
        # Fallback when LLM is unavailable.
        answer = fallback_rag_style_reply(payload.message, context, payload.language)
        if not context:
            answer = generate_chat_reply(payload.message, payload.language)
    save_chat_message(
        {
            "user_message": payload.message,
            "assistant_message": answer,
            "language": payload.language,
        }
    )
    return ChatOut(response=answer, sources=sources)


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


@app.delete("/api/itineraries/{itinerary_id}")
def remove_itinerary(itinerary_id: int):
    ok = delete_itinerary(itinerary_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Could not delete itinerary")
    return {"success": True}


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

    # Whisper needs ffmpeg executable. If system ffmpeg is missing, use
    # imageio-ffmpeg bundled binary automatically.
    try:
        import imageio_ffmpeg  # type: ignore

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = str(Path(ffmpeg_exe).parent)
        local_ffmpeg = BASE_DIR / "ffmpeg.exe"
        if not local_ffmpeg.exists() and Path(ffmpeg_exe).exists():
            # Whisper calls "ffmpeg" directly; keep a local executable alias.
            shutil.copyfile(ffmpeg_exe, local_ffmpeg)
        current_path = os.environ.get("PATH", "")
        if ffmpeg_dir and ffmpeg_dir not in current_path:
            os.environ["PATH"] = str(BASE_DIR) + os.pathsep + ffmpeg_dir + os.pathsep + current_path
    except Exception:
        pass

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
