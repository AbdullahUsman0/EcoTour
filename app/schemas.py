from pydantic import BaseModel, Field


class TripRequestIn(BaseModel):
    origin: str = Field(min_length=2, max_length=120)
    destination: str = Field(min_length=2, max_length=120)
    budget: float = Field(gt=0)
    travelers: int = Field(default=1, ge=1, le=20)
    language: str = Field(default="en")
    hotel_tier: str = Field(default="midrange")
    transport_mode: str = Field(default="mixed")
    activity_pace: str = Field(default="balanced")
    food_style: str = Field(default="local")


class TripOption(BaseModel):
    title: str
    estimated_cost: float
    highlights: list[str]


class TripResponse(BaseModel):
    route: str
    distance_km: float
    estimated_cost: float
    budget_fit: str
    weather_note: str
    fare_note: str
    plan: list[str]
    options: list[TripOption] = []
    do_now: list[str] = []
    avoid_now: list[str] = []


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en")


class ChatOut(BaseModel):
    response: str
    sources: list[str] = []


class SpeakIn(BaseModel):
    text: str = Field(min_length=1, max_length=1500)


class CrisisIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en")


class CrisisOut(BaseModel):
    severity: str
    advice: str
    helpline: str


class ItinerarySaveIn(BaseModel):
    traveler_name: str = Field(min_length=2, max_length=120)
    route: str = Field(min_length=3, max_length=240)
    estimated_cost: float = Field(gt=0)
    budget_fit: str = Field(min_length=2, max_length=80)
    plan: list[str] = Field(min_length=1, max_length=10)


class ItineraryOut(BaseModel):
    id: int
    traveler_name: str
    route: str
    estimated_cost: float
    budget_fit: str
    plan: list[str]
    created_at: str


class TripHistoryOut(BaseModel):
    id: int
    origin: str
    destination: str
    estimated_cost: float
    budget: float
    created_at: str
