from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Booking, Trek, User
from schemas import BookingCreate, BookingResponse
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .all()
    )


@router.get("/all", response_model=list[BookingResponse])
def get_all_bookings(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return db.query(Booking).all()


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trek = db.query(Trek).filter(Trek.id == booking_in.trek_id, Trek.is_active == True).first()
    if not trek:
        raise HTTPException(status_code=404, detail="Trek not found or inactive")

    spots_left = trek.max_participants - trek.current_bookings
    if booking_in.num_participants > spots_left:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough spots available. Only {spots_left} spots left.",
        )

    total_price = trek.price_per_person * booking_in.num_participants
    booking = Booking(
        user_id=current_user.id,
        trek_id=booking_in.trek_id,
        trek_date=booking_in.trek_date,
        num_participants=booking_in.num_participants,
        total_price=total_price,
        special_requirements=booking_in.special_requirements,
    )
    trek.current_bookings += booking_in.num_participants
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    return booking


@router.put("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    booking.status = "cancelled"
    trek = db.query(Trek).filter(Trek.id == booking.trek_id).first()
    if trek:
        trek.current_bookings = max(0, trek.current_bookings - booking.num_participants)
    db.commit()
    db.refresh(booking)
    return booking
