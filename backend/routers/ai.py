import os
import json
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Trek
from schemas import (
    AnalyzeTrekRequest,
    RecommendGearRequest,
    TrailStoryRequest,
    FitnessPlanRequest,
    ChatRequest,
    PredictDifficultyRequest,
)

router = APIRouter(prefix="/ai", tags=["ai"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Lazy-initialise the Gemini client so we don't blow up when no key is set.
_genai_model = None


def _get_model():
    global _genai_model
    if _genai_model is not None:
        return _genai_model
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _genai_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        _genai_model = None
    return _genai_model


def _call_gemini(prompt: str) -> Optional[str]:
    model = _get_model()
    if model is None:
        return None
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return None


def _trek_or_404(trek_id: int, db: Session) -> Trek:
    trek = db.query(Trek).filter(Trek.id == trek_id).first()
    if not trek:
        raise HTTPException(status_code=404, detail="Trek not found")
    return trek


# ─── 1. Analyze Trek ──────────────────────────────────────────────────────────

@router.post("/analyze-trek")
def analyze_trek(req: AnalyzeTrekRequest, db: Session = Depends(get_db)):
    trek = _trek_or_404(req.trek_id, db)

    prompt = f"""
You are a professional trekking analyst. Analyze this trek and respond ONLY with valid JSON.

Trek Details:
- Name: {trek.name}
- Location: {trek.location}, {trek.region}
- Difficulty: {trek.difficulty}
- Duration: {trek.duration_days} days
- Distance: {trek.distance_km} km
- Elevation Gain: {trek.elevation_gain_m} m
- Max Altitude: {trek.max_altitude_m} m
- Season: {trek.season}

Return JSON with exactly these keys:
{{
  "difficulty_analysis": "detailed analysis string",
  "risk_level": "Low | Moderate | High | Extreme",
  "fitness_requirements": "fitness requirements string",
  "best_months": ["Month1", "Month2"],
  "ai_summary": "vivid 2-3 sentence poetic description of the trek"
}}
"""

    raw = _call_gemini(prompt)
    if raw:
        try:
            # Strip markdown code fences if present
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            result = json.loads(cleaned)
        except Exception:
            result = None
    else:
        result = None

    if not result:
        result = {
            "difficulty_analysis": f"{trek.name} is a {trek.difficulty} trek spanning {trek.duration_days} days over {trek.distance_km} km with {trek.elevation_gain_m}m of elevation gain. It demands solid cardiovascular endurance and prior trekking experience.",
            "risk_level": "High" if trek.difficulty == "hard" else "Moderate" if trek.difficulty == "moderate" else "Low",
            "fitness_requirements": "Regular cardio (running/cycling), leg-strength training, and 3–4 practice hikes on uneven terrain recommended before attempting this trek.",
            "best_months": ["May", "June", "September", "October"],
            "ai_summary": f"The {trek.name} trail winds through the breathtaking landscapes of {trek.region}, challenging trekkers with {trek.elevation_gain_m}m of ascent over {trek.distance_km} km. At its zenith of {trek.max_altitude_m}m, the horizon dissolves into a canvas of peaks and sky. This is not merely a trek — it is a conversation with the mountains.",
        }

    # Persist ai_summary back to the trek record
    trek.ai_summary = result.get("ai_summary", trek.ai_summary)
    db.commit()

    return result


# ─── 2. Recommend Gear ────────────────────────────────────────────────────────

@router.post("/recommend-gear")
def recommend_gear(req: RecommendGearRequest, db: Session = Depends(get_db)):
    trek = _trek_or_404(req.trek_id, db)

    prompt = f"""
You are an expert trekking gear consultant. Recommend gear for this trek and respond ONLY with valid JSON.

Trek: {trek.name} ({trek.difficulty}, {trek.duration_days} days, max altitude {trek.max_altitude_m}m)
User level: {req.user_level}
Expected weather: {req.weather}

Return JSON as a list of gear items. Each item must have:
- "category": one of Clothing, Footwear, Navigation, Safety, Nutrition, Shelter, Electronics
- "item": item name
- "essential": true or false
- "reasoning": short explanation

Return format: {{"gear": [...]}}
"""

    raw = _call_gemini(prompt)
    if raw:
        try:
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            result = json.loads(cleaned)
        except Exception:
            result = None
    else:
        result = None

    if not result:
        result = {
            "gear": [
                {"category": "Clothing", "item": "Moisture-wicking base layer", "essential": True, "reasoning": "Keeps sweat away from skin to prevent chills at altitude."},
                {"category": "Clothing", "item": "Insulated down jacket", "essential": True, "reasoning": f"Temperatures at {trek.max_altitude_m}m can drop sharply after sunset."},
                {"category": "Clothing", "item": "Waterproof rain jacket", "essential": True, "reasoning": "Unexpected showers are common in mountain terrain."},
                {"category": "Footwear", "item": "High-ankle trekking boots", "essential": True, "reasoning": "Ankle support is critical on rocky, uneven trails."},
                {"category": "Footwear", "item": "Gaiters", "essential": False, "reasoning": "Useful for snow patches and muddy sections."},
                {"category": "Navigation", "item": "Offline map (Maps.me / Gaia GPS)", "essential": True, "reasoning": "No cellular signal on most mountain trails."},
                {"category": "Navigation", "item": "Compass", "essential": True, "reasoning": "Backup navigation in case of device failure."},
                {"category": "Safety", "item": "First aid kit", "essential": True, "reasoning": "Essential for treating blisters, cuts, and minor injuries."},
                {"category": "Safety", "item": "Altitude sickness medication (Diamox)", "essential": True if trek.max_altitude_m > 3500 else False, "reasoning": "Preventive medication for altitude sickness above 3500m."},
                {"category": "Nutrition", "item": "High-energy trail mix & bars", "essential": True, "reasoning": "Quick carbohydrates sustain energy on long hiking days."},
                {"category": "Nutrition", "item": "Electrolyte sachets", "essential": True, "reasoning": "Replenishes salts lost through heavy sweating."},
                {"category": "Shelter", "item": "Sleeping bag (-10°C rated)", "essential": True, "reasoning": "Night temperatures at high camps can be extreme."},
                {"category": "Shelter", "item": "Emergency bivy sack", "essential": False, "reasoning": "Lightweight emergency shelter if caught out overnight."},
                {"category": "Electronics", "item": "Headlamp with extra batteries", "essential": True, "reasoning": "Early alpine starts and long days make a headlamp indispensable."},
                {"category": "Electronics", "item": "Power bank (20,000 mAh)", "essential": True, "reasoning": "No charging points on the trail; cold temperatures drain batteries faster."},
            ],
            "trek": trek.name,
            "user_level": req.user_level,
            "weather": req.weather,
        }

    return result


# ─── 3. Trail Story ───────────────────────────────────────────────────────────

@router.post("/trail-story")
def trail_story(req: TrailStoryRequest, db: Session = Depends(get_db)):
    trek = _trek_or_404(req.trek_id, db)

    prompt = f"""
Write an epic, immersive 3-paragraph narrative travel story about the {trek.name} trek in {trek.region}, India.
Style: National Geographic feature — poetic, vivid, sensory, awe-inspiring.
Include: the journey start, the landscape, the summit or highlight moment.
Trek facts: {trek.duration_days} days, {trek.distance_km} km, max altitude {trek.max_altitude_m}m.
Do not use any JSON formatting — just pure, beautiful prose.
"""

    story = _call_gemini(prompt)

    if not story:
        story = (
            f"The trail to {trek.name} begins where the paved world surrenders to stone. "
            f"At the trailhead in {trek.location}, the air already carries the mineral whisper of glaciers — "
            f"cool, ancient, insistent. Rhododendron forests blaze crimson and white along the lower ridges, "
            f"their blossoms shivering in the wind that descends from the high passes. "
            f"Your boots find the rhythm of ascent, each step a small negotiation with gravity.\n\n"
            f"As the treeline falls away, the world opens. The {trek.region} reveals itself in panoramic grandeur — "
            f"a cathedral of peaks stretching to horizons that seem borrowed from myth. "
            f"The trail grows steeper now, switchbacking across scree fields dusted with the remnants of last winter's snow. "
            f"Altitude presses gently on the lungs, a reminder that at {trek.max_altitude_m} metres, "
            f"the atmosphere is a gift given in smaller portions.\n\n"
            f"The summit arrives not with fanfare but with silence. A profound, reverberating silence "
            f"that only the high mountains can produce. Standing at the apex of {trek.name}, "
            f"with {trek.distance_km} kilometres of trail behind you and the whole of {trek.region} spread below, "
            f"you understand why trekkers return again and again to these heights — "
            f"not merely for the views, but for the version of themselves they discover along the way."
        )

    return {"trek": trek.name, "story": story}


# ─── 4. Fitness Plan ──────────────────────────────────────────────────────────

@router.post("/fitness-plan")
def fitness_plan(req: FitnessPlanRequest, db: Session = Depends(get_db)):
    trek = _trek_or_404(req.trek_id, db)

    prompt = f"""
Create a detailed week-by-week fitness training plan for the {trek.name} trek.

Trek details: {trek.difficulty} difficulty, {trek.duration_days} days, {trek.distance_km}km, max altitude {trek.max_altitude_m}m.
User fitness level: {req.fitness_level}
Weeks available: {req.weeks_to_trek}

Respond ONLY with valid JSON:
{{
  "overview": "brief plan summary",
  "weekly_plan": [
    {{
      "week": 1,
      "focus": "weekly theme",
      "exercises": ["exercise 1", "exercise 2"],
      "long_hike_km": 5,
      "tips": "week tip"
    }}
  ],
  "nutrition_advice": "general nutrition advice",
  "gear_training": "advice on training with gear"
}}
"""

    raw = _call_gemini(prompt)
    if raw:
        try:
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            result = json.loads(cleaned)
        except Exception:
            result = None
    else:
        result = None

    if not result:
        weeks = min(req.weeks_to_trek, 12)
        weekly_plan = []
        for w in range(1, weeks + 1):
            phase = "Base Building" if w <= weeks // 3 else "Strength & Endurance" if w <= (weeks * 2) // 3 else "Peak & Taper"
            weekly_plan.append({
                "week": w,
                "focus": phase,
                "exercises": [
                    f"5km run at comfortable pace ({2 + w} days/week)",
                    "Stair climbing 20 min",
                    "Squats and lunges 3×15",
                    "Core plank 3×60 sec",
                ],
                "long_hike_km": min(5 + w * 2, 25),
                "tips": f"Week {w}: Focus on consistency over intensity. Sleep and recovery are as important as training.",
            })
        result = {
            "overview": f"A {weeks}-week progressive training plan for {trek.name}. Designed for a {req.fitness_level} athlete with {req.weeks_to_trek} weeks to prepare.",
            "weekly_plan": weekly_plan,
            "nutrition_advice": "Prioritise complex carbohydrates (oats, sweet potato, brown rice) for sustained energy. Aim for 1.6–2g of protein per kg bodyweight for muscle recovery.",
            "gear_training": "Train with your actual trekking boots from Week 2 to prevent blisters. Carry a loaded backpack (8–10kg) on all long hikes.",
        }

    return result


# ─── 5. Chat (Summit, your AI guide) ─────────────────────────────────────────

@router.post("/chat")
def chat(req: ChatRequest):
    context_block = f"\nContext: {req.context}" if req.context else ""
    prompt = f"""
You are Summit, a friendly and expert AI trekking guide. You have decades of experience leading expeditions across the Himalayas, Sahyadris, and beyond.
Respond to the user's message in under 200 words. Be warm, knowledgeable, practical, and inspiring.{context_block}

User: {req.message}
Summit:"""

    reply = _call_gemini(prompt)

    if not reply:
        reply = (
            "Hey there, fellow adventurer! I'm Summit, your AI trekking guide. "
            "I'd love to help you plan your next mountain adventure — from gear selection "
            "and fitness prep to route planning and altitude acclimatisation. "
            "Whether you're a first-timer or a seasoned alpinist, the mountains have something "
            "new to teach every time. What would you like to know? 🏔️"
        )

    return {"response": reply.strip(), "guide": "Summit"}


# ─── 6. Predict Difficulty ────────────────────────────────────────────────────

@router.post("/predict-difficulty")
def predict_difficulty(req: PredictDifficultyRequest):
    prompt = f"""
Analyse a trek with these metrics and respond ONLY with valid JSON:
- Elevation gain: {req.elevation_gain}m
- Distance: {req.distance_km}km
- Duration: {req.duration_days} days
- Max altitude: {req.max_altitude}m

Return JSON:
{{
  "score": <integer 0-100>,
  "difficulty_label": "Easy | Moderate | Hard | Extreme",
  "key_factors": ["factor1", "factor2", "factor3"],
  "training_advice": "personalised training advice string"
}}
"""

    raw = _call_gemini(prompt)
    if raw:
        try:
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            result = json.loads(cleaned)
        except Exception:
            result = None
    else:
        result = None

    if not result:
        # Algorithmic fallback
        score = 0
        score += min(40, int(req.elevation_gain / 100))   # up to 40 pts
        score += min(20, int(req.distance_km / 5))         # up to 20 pts
        score += min(20, int(req.max_altitude / 500))      # up to 20 pts
        score += min(20, 20 - req.duration_days * 2)       # shorter = harder per day
        score = max(0, min(100, score))

        if score <= 25:
            label = "Easy"
        elif score <= 50:
            label = "Moderate"
        elif score <= 75:
            label = "Hard"
        else:
            label = "Extreme"

        result = {
            "score": score,
            "difficulty_label": label,
            "key_factors": [
                f"Elevation gain of {req.elevation_gain}m is {'significant' if req.elevation_gain > 1500 else 'manageable'}",
                f"Maximum altitude of {req.max_altitude}m {'requires acclimatisation' if req.max_altitude > 3500 else 'is below the altitude sickness threshold'}",
                f"Daily distance of {req.distance_km / max(req.duration_days,1):.1f}km/day is {'demanding' if req.distance_km / max(req.duration_days,1) > 12 else 'moderate'}",
            ],
            "training_advice": f"For a {label.lower()} trek, focus on cardiovascular endurance, leg strength, and 3–4 practice hikes before departure.",
        }

    return result


# ─── 7. Daily Tip ─────────────────────────────────────────────────────────────

@router.get("/daily-tip")
def daily_tip():
    today = date.today().isoformat()
    prompt = f"""
Today is {today}. Generate a unique, practical trekking tip for this date.
Respond ONLY with valid JSON:
{{
  "tip": "the tip text (1-3 sentences)",
  "category": "one of: Safety, Nutrition, Gear, Training, Navigation, Mental Health, Environment",
  "date": "{today}"
}}
"""

    raw = _call_gemini(prompt)
    if raw:
        try:
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            result = json.loads(cleaned)
        except Exception:
            result = None
    else:
        result = None

    if not result:
        tips_pool = [
            ("Start every trekking day with 500ml of water before you eat. Altitude dehydration is subtle and significantly impacts energy and judgement.", "Nutrition"),
            ("Always tell someone your planned route and expected return time before heading out — even on well-marked trails.", "Safety"),
            ("Break in new boots on shorter walks for at least 4 weeks before any multi-day trek. Blisters on Day 1 can ruin the entire journey.", "Gear"),
            ("The 'rest step' technique — locking your rear knee briefly with each uphill step — dramatically reduces fatigue on long ascents.", "Training"),
            ("Download offline maps before you leave civilisation. Apps like Gaia GPS and Maps.me work without cell signal.", "Navigation"),
            ("On tough days, focus only on the next 100 metres, not the summit. Breaking the journey into tiny goals keeps you moving.", "Mental Health"),
            ("Pack out everything you pack in. Leave the trail cleaner than you found it — even pick up others' litter when you can.", "Environment"),
        ]
        from hashlib import md5
        idx = int(md5(today.encode()).hexdigest(), 16) % len(tips_pool)
        tip_text, category = tips_pool[idx]
        result = {"tip": tip_text, "category": category, "date": today}

    return result
