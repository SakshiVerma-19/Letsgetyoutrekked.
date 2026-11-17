from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_admin: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# ─── Trek Schemas ─────────────────────────────────────────────────────────────

class TrekCreate(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: str
    duration_days: int
    distance_km: float
    elevation_gain_m: float
    max_altitude_m: float
    price_per_person: float
    location: str
    region: str
    season: Optional[str] = None
    max_participants: int = 20
    image_url: Optional[str] = None


class TrekUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    duration_days: Optional[int] = None
    distance_km: Optional[float] = None
    elevation_gain_m: Optional[float] = None
    max_altitude_m: Optional[float] = None
    price_per_person: Optional[float] = None
    location: Optional[str] = None
    region: Optional[str] = None
    season: Optional[str] = None
    max_participants: Optional[int] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    ai_summary: Optional[str] = None


class TrekResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    difficulty: str
    duration_days: int
    distance_km: float
    elevation_gain_m: float
    max_altitude_m: float
    price_per_person: float
    location: str
    region: str
    season: Optional[str]
    max_participants: int
    current_bookings: int
    is_active: bool
    image_url: Optional[str]
    ai_summary: Optional[str]
    created_at: datetime


# ─── Booking Schemas ───────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    trek_id: int
    trek_date: datetime
    num_participants: int
    special_requirements: Optional[str] = None


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    special_requirements: Optional[str] = None


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    trek_id: int
    booking_date: datetime
    trek_date: datetime
    num_participants: int
    total_price: float
    status: str
    special_requirements: Optional[str]
    created_at: datetime
    trek: Optional[TrekResponse] = None


# ─── Review Schemas ────────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    trek_id: int
    rating: int
    comment: Optional[str]
    ai_sentiment_score: Optional[float]
    created_at: datetime
    user: Optional[UserResponse] = None


# ─── GearItem Schemas ──────────────────────────────────────────────────────────

class GearItemCreate(BaseModel):
    trek_id: int
    item_name: str
    category: str
    is_essential: bool = True
    ai_recommended: bool = False


class GearItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trek_id: int
    item_name: str
    category: str
    is_essential: bool
    ai_recommended: bool


# ─── AI Request Schemas ────────────────────────────────────────────────────────

class AnalyzeTrekRequest(BaseModel):
    trek_id: int


class RecommendGearRequest(BaseModel):
    trek_id: int
    user_level: str
    weather: str


class TrailStoryRequest(BaseModel):
    trek_id: int


class FitnessPlanRequest(BaseModel):
    trek_id: int
    fitness_level: str
    weeks_to_trek: int


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class PredictDifficultyRequest(BaseModel):
    elevation_gain: int
    distance_km: float
    duration_days: int
    max_altitude: int
