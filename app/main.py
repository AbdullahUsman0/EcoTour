from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.data.knowledge import EMERGENCY_CONTACTS
from app.models import ChatMessage, TripRequest
from app.schemas import ChatIn, ChatOut, CrisisIn, CrisisOut, TripRequestIn, TripResponse
from app.services.chat import generate_chat_reply
from app.services.crisis import crisis_response
from app.services.planner import budget_message, create_plan, estimate_trip_cost, haversine_distance_km

app = FastAPI(title="EcoTour AI Pakistan")
Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/")
def root():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.post("/api/plan-trip", response_model=TripResponse)
def plan_trip(payload: TripRequestIn, db: Session = Depends(get_db)):
    distance = haversine_distance_km(payload.origin, payload.destination)
    if distance == 0.0:
        raise HTTPException(
            status_code=400,
            detail="Unknown city. Try Islamabad, Lahore, Karachi, Murree, Hunza, Gilgit, or Skardu.",
        )
    estimated_cost = estimate_trip_cost(distance, payload.travelers)
    db_row = TripRequest(
        origin=payload.origin,
        destination=payload.destination,
        budget=payload.budget,
        travelers=payload.travelers,
        language=payload.language,
        estimated_distance_km=distance,
        estimated_cost=estimated_cost,
    )
    db.add(db_row)
    db.commit()
    return TripResponse(
        route=f"{payload.origin.title()} -> {payload.destination.title()}",
        distance_km=round(distance, 1),
        estimated_cost=estimated_cost,
        budget_fit=budget_message(estimated_cost, payload.budget),
        plan=create_plan(payload.destination),
    )


@app.post("/api/chat", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db)):
    answer = generate_chat_reply(payload.message, payload.language)
    db.add(
        ChatMessage(
            user_message=payload.message,
            assistant_message=answer,
            language=payload.language,
        )
    )
    db.commit()
    return ChatOut(response=answer)


@app.post("/api/crisis", response_model=CrisisOut)
def crisis(payload: CrisisIn):
    severity, advice, helpline = crisis_response(payload.message, payload.language)
    return CrisisOut(severity=severity, advice=advice, helpline=helpline)


@app.get("/api/emergency")
def emergency_contacts():
    return {"contacts": EMERGENCY_CONTACTS}


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
