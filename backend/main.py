import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import engine, SessionLocal
from models import Base, Trek
from routers import users, treks, bookings, ai

SEED_TREKS = [
    {
        "name": "Roopkund",
        "description": "The mysterious Skeleton Lake trek, one of India's most dramatic high-altitude trails.",
        "difficulty": "hard",
        "duration_days": 8,
        "distance_km": 53.0,
        "elevation_gain_m": 2350.0,
        "max_altitude_m": 5029.0,
        "price_per_person": 12000.0,
        "location": "Chamoli",
        "region": "Uttarakhand",
        "season": "May-June, September-October",
        "max_participants": 15,
    },
    {
        "name": "Valley of Flowers",
        "description": "A UNESCO World Heritage Site bursting with rare Himalayan flora in a breathtaking alpine valley.",
        "difficulty": "easy",
        "duration_days": 6,
        "distance_km": 38.0,
        "elevation_gain_m": 1100.0,
        "max_altitude_m": 3658.0,
        "price_per_person": 8000.0,
        "location": "Chamoli",
        "region": "Uttarakhand",
        "season": "July-September",
        "max_participants": 25,
    },
    {
        "name": "Hampta Pass",
        "description": "A dramatic crossover trek connecting the lush Kullu valley to the stark Spiti desert landscape.",
        "difficulty": "moderate",
        "duration_days": 5,
        "distance_km": 35.0,
        "elevation_gain_m": 1500.0,
        "max_altitude_m": 4270.0,
        "price_per_person": 9500.0,
        "location": "Kullu",
        "region": "Himachal Pradesh",
        "season": "June-October",
        "max_participants": 20,
    },
    {
        "name": "Kedarkantha",
        "description": "A beloved winter summit trek offering spectacular 360° views of Himalayan peaks from its snow-laden top.",
        "difficulty": "easy",
        "duration_days": 6,
        "distance_km": 20.0,
        "elevation_gain_m": 1100.0,
        "max_altitude_m": 3810.0,
        "price_per_person": 7500.0,
        "location": "Uttarkashi",
        "region": "Uttarakhand",
        "season": "December-April",
        "max_participants": 25,
    },
    {
        "name": "Chopta Chandrashila",
        "description": "The 'Mini Switzerland of Uttarakhand', featuring pristine meadows and a sacred summit temple.",
        "difficulty": "moderate",
        "duration_days": 4,
        "distance_km": 14.0,
        "elevation_gain_m": 900.0,
        "max_altitude_m": 4090.0,
        "price_per_person": 6000.0,
        "location": "Rudraprayag",
        "region": "Uttarakhand",
        "season": "March-June, September-November",
        "max_participants": 20,
    },
    {
        "name": "Sandakphu",
        "description": "The highest peak in West Bengal, offering the only vantage point to see four of the five highest peaks in the world.",
        "difficulty": "moderate",
        "duration_days": 7,
        "distance_km": 55.0,
        "elevation_gain_m": 2130.0,
        "max_altitude_m": 3636.0,
        "price_per_person": 8500.0,
        "location": "Darjeeling",
        "region": "West Bengal",
        "season": "October-December, March-May",
        "max_participants": 20,
    },
    {
        "name": "Dzukou Valley",
        "description": "The 'Valley of Flowers of the Northeast', a hidden paradise straddling the Nagaland-Manipur border.",
        "difficulty": "easy",
        "duration_days": 4,
        "distance_km": 24.0,
        "elevation_gain_m": 600.0,
        "max_altitude_m": 2452.0,
        "price_per_person": 5500.0,
        "location": "Kohima",
        "region": "Nagaland",
        "season": "June-September",
        "max_participants": 20,
    },
    {
        "name": "Pin Bhaba Pass",
        "description": "A remote, awe-inspiring crossover trek from the verdant Kinnaur forests to the barren moonscapes of Spiti.",
        "difficulty": "hard",
        "duration_days": 7,
        "distance_km": 65.0,
        "elevation_gain_m": 1850.0,
        "max_altitude_m": 5319.0,
        "price_per_person": 14000.0,
        "location": "Kinnaur",
        "region": "Himachal Pradesh",
        "season": "July-September",
        "max_participants": 12,
    },
    {
        "name": "Rupin Pass",
        "description": "Consistently ranked among India's best treks, featuring waterfalls, snow bridges, and dramatic hanging villages.",
        "difficulty": "hard",
        "duration_days": 8,
        "distance_km": 52.0,
        "elevation_gain_m": 2000.0,
        "max_altitude_m": 4650.0,
        "price_per_person": 13000.0,
        "location": "Uttarkashi",
        "region": "Uttarakhand",
        "season": "May-June, September-October",
        "max_participants": 15,
    },
    {
        "name": "Har Ki Dun",
        "description": "The 'Valley of Gods' — an ancient cradle of mythology amid glaciers, moraines, and rhododendron forests.",
        "difficulty": "easy",
        "duration_days": 7,
        "distance_km": 46.0,
        "elevation_gain_m": 1200.0,
        "max_altitude_m": 3566.0,
        "price_per_person": 7000.0,
        "location": "Uttarkashi",
        "region": "Uttarakhand",
        "season": "April-June, September-November",
        "max_participants": 25,
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Seed treks if none exist
    db = SessionLocal()
    try:
        if db.query(Trek).count() == 0:
            for trek_data in SEED_TREKS:
                db.add(Trek(**trek_data))
            db.commit()
    finally:
        db.close()

    yield  # App is running


app = FastAPI(
    title="Trek Management System",
    description=(
        "A comprehensive platform for discovering, booking, and managing treks across India. "
        "Powered by FastAPI, SQLAlchemy, and Gemini AI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api")
app.include_router(treks.router, prefix="/api")
app.include_router(bookings.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Trek Management API", "docs": "/docs", "version": "1.0.0"}
