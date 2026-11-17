from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("TrekReview", back_populates="user")


class Trek(Base):
    __tablename__ = "treks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    difficulty = Column(String, nullable=False)  # easy, moderate, hard
    duration_days = Column(Integer, nullable=False)
    distance_km = Column(Float, nullable=False)
    elevation_gain_m = Column(Float, nullable=False)
    max_altitude_m = Column(Float, nullable=False)
    price_per_person = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    region = Column(String, nullable=False)
    season = Column(String, nullable=True)
    max_participants = Column(Integer, default=20)
    current_bookings = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bookings = relationship("Booking", back_populates="trek")
    reviews = relationship("TrekReview", back_populates="trek")
    gear_items = relationship("GearItem", back_populates="trek")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trek_id = Column(Integer, ForeignKey("treks.id"), nullable=False)
    booking_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    trek_date = Column(DateTime, nullable=False)
    num_participants = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="confirmed")  # confirmed, cancelled, completed
    special_requirements = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="bookings")
    trek = relationship("Trek", back_populates="bookings")


class TrekReview(Base):
    __tablename__ = "trek_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trek_id = Column(Integer, ForeignKey("treks.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    ai_sentiment_score = Column(Float, nullable=True)  # 0.0 to 1.0
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reviews")
    trek = relationship("Trek", back_populates="reviews")


class GearItem(Base):
    __tablename__ = "gear_items"

    id = Column(Integer, primary_key=True, index=True)
    trek_id = Column(Integer, ForeignKey("treks.id"), nullable=False)
    item_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    is_essential = Column(Boolean, default=True)
    ai_recommended = Column(Boolean, default=False)

    trek = relationship("Trek", back_populates="gear_items")
