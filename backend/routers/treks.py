from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Trek, TrekReview, User
from schemas import TrekCreate, TrekUpdate, TrekResponse, ReviewCreate, ReviewResponse
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/treks", tags=["treks"])


@router.get("", response_model=list[TrekResponse])
def list_treks(
    difficulty: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Trek).filter(Trek.is_active == True)
    if difficulty:
        q = q.filter(Trek.difficulty == difficulty.lower())
    if region:
        q = q.filter(Trek.region.ilike(f"%{region}%"))
    if search:
        q = q.filter(
            Trek.name.ilike(f"%{search}%") | Trek.description.ilike(f"%{search}%")
        )
    return q.offset(skip).limit(limit).all()


@router.get("/{trek_id}", response_model=TrekResponse)
def get_trek(trek_id: int, db: Session = Depends(get_db)):
    trek = db.query(Trek).filter(Trek.id == trek_id).first()
    if not trek:
        raise HTTPException(status_code=404, detail="Trek not found")
    return trek


@router.post("", response_model=TrekResponse, status_code=status.HTTP_201_CREATED)
def create_trek(
    trek_in: TrekCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    trek = Trek(**trek_in.model_dump())
    db.add(trek)
    db.commit()
    db.refresh(trek)
    return trek


@router.put("/{trek_id}", response_model=TrekResponse)
def update_trek(
    trek_id: int,
    trek_in: TrekUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    trek = db.query(Trek).filter(Trek.id == trek_id).first()
    if not trek:
        raise HTTPException(status_code=404, detail="Trek not found")
    for field, value in trek_in.model_dump(exclude_unset=True).items():
        setattr(trek, field, value)
    db.commit()
    db.refresh(trek)
    return trek


@router.delete("/{trek_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trek(
    trek_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    trek = db.query(Trek).filter(Trek.id == trek_id).first()
    if not trek:
        raise HTTPException(status_code=404, detail="Trek not found")
    trek.is_active = False
    db.commit()


@router.get("/{trek_id}/reviews", response_model=list[ReviewResponse])
def get_reviews(trek_id: int, db: Session = Depends(get_db)):
    trek = db.query(Trek).filter(Trek.id == trek_id).first()
    if not trek:
        raise HTTPException(status_code=404, detail="Trek not found")
    return (
        db.query(TrekReview)
        .filter(TrekReview.trek_id == trek_id)
        .all()
    )


@router.post("/{trek_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    trek_id: int,
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trek = db.query(Trek).filter(Trek.id == trek_id).first()
    if not trek:
        raise HTTPException(status_code=404, detail="Trek not found")

    existing = (
        db.query(TrekReview)
        .filter(TrekReview.trek_id == trek_id, TrekReview.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this trek")

    review = TrekReview(
        user_id=current_user.id,
        trek_id=trek_id,
        rating=review_in.rating,
        comment=review_in.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
