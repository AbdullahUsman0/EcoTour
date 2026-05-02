from pydantic import BaseModel, Field


class TripRequestIn(BaseModel):
    origin: str = Field(min_length=2, max_length=120)
    destination: str = Field(min_length=2, max_length=120)
    budget: float = Field(gt=0)
    travelers: int = Field(default=1, ge=1, le=20)
    language: str = Field(default="en")


class TripResponse(BaseModel):
    route: str
    distance_km: float
    estimated_cost: float
    budget_fit: str
    plan: list[str]


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en")


class ChatOut(BaseModel):
    response: str


class CrisisIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en")


class CrisisOut(BaseModel):
    severity: str
    advice: str
    helpline: str
