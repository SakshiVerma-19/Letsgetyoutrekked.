# 🏔️ TrekVerse — AI-Powered Trek Management Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)](https://sqlite.org/)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-1.5_Flash-4285F4?style=for-the-badge&logo=google)](https://aistudio.google.com/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3-06B6D4?style=for-the-badge&logo=tailwindcss)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)](https://docker.com/)

> A full-stack trek management platform powered by **Google Gemini AI** — book hikes, generate trail stories, get AI gear lists, predict difficulty scores, and train with personalized fitness plans.

---

## ✨ Features

### 🗺️ Core Platform
- **Trek Catalog** — Browse, search, and filter treks by difficulty, region, altitude, and season
- **Smart Bookings** — Book treks with participant management and real-time availability checks
- **User Authentication** — JWT-secured auth with role-based access (admin / user)
- **Reviews & Ratings** — Leave reviews with AI-powered sentiment analysis
- **Admin Dashboard** — Full CRUD management for treks, bookings, and users

### 🤖 AI-Powered Features (7 Endpoints)
1. **Trek Analyzer** — Gemini AI deep-dives trek data for risk level, fitness needs & best months
2. **Gear Recommender** — Smart, categorized gear lists based on trek + user experience + weather
3. **Trail Story Generator** — National Geographic-style immersive 3-paragraph trek narratives
4. **Fitness Plan Builder** — Week-by-week personalized training schedule to summit-ready fitness
5. **Summit AI Chat** — "Summit", your expert AI trekking guide chatbot
6. **Difficulty Predictor** — ML-style score (0–100) from elevation, distance, duration & altitude
7. **Daily Trek Tip** — Fresh AI trekking wisdom delivered every day

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                        │
│  React 18 + Vite + TailwindCSS + Framer Motion + Zustand    │
│  http://localhost:5173                                       │
└────────────────────────┬────────────────────────────────────┘
                         │  HTTP / REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                          │
│  Python 3.11 · SQLAlchemy · JWT Auth · Pydantic             │
│  http://localhost:8000                                       │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ /treks   │ │/bookings │ │ /users   │ │  /ai  (×7)   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────┬───────┘  │
└──────────────────────────────────────────────────┼──────────┘
                                                   │
                         ┌─────────────────────────▼─────────┐
                         │       GOOGLE GEMINI AI              │
                         │   gemini-1.5-flash model            │
                         │   (Graceful mock if no key)         │
                         └─────────────────────────────────────┘
                         │
        ┌────────────────▼─────────────────┐
        │          SQLite Database          │
        │   trek_management.db             │
        │   Users · Treks · Bookings       │
        │   Reviews · GearItems            │
        └───────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- (Optional) [Google AI Studio API Key](https://aistudio.google.com/) for live AI features

### 1. Clone the repository
```bash
git clone <repo-url>
cd "trek management"
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your-gemini-api-key-from-aistudio-google-com
```

> **Note:** The app works without a Gemini API key — AI endpoints return creative mock responses as fallback.

### 4. Start the Backend
```bash
uvicorn main:app --reload --port 8000
```
Backend runs at **http://localhost:8000**  
Swagger docs at **http://localhost:8000/docs**

### 5. Frontend Setup
```bash
cd ../frontend
npm install
```

### 6. Start the Frontend
```bash
npm run dev
```
Frontend runs at **http://localhost:5173**

---

## 🤖 AI Features Deep Dive

| Endpoint | Method | Description |
|---|---|---|
| `/api/ai/analyze-trek` | POST | Comprehensive trek analysis — risk, fitness needs, best months, vivid AI summary |
| `/api/ai/recommend-gear` | POST | Categorized gear list (7 categories) with AI reasoning per item |
| `/api/ai/trail-story` | POST | 3-paragraph immersive narrative written like a National Geographic feature |
| `/api/ai/fitness-plan` | POST | Week-by-week training schedule with exercises, distances, and expert tips |
| `/api/ai/chat` | POST | Chat with "Summit" — your friendly AI trekking expert (< 200 words/reply) |
| `/api/ai/predict-difficulty` | POST | Difficulty score 0–100 from elevation gain, distance, duration, altitude |
| `/api/ai/daily-tip` | GET | Today's AI trekking wisdom with category badge |

All AI endpoints gracefully fall back to rich mock responses when `GEMINI_API_KEY` is not set.

---

## 🔐 Default Admin Credentials

| Field | Value |
|---|---|
| Email | `admin@trekverse.com` |
| Password | `admin123` |

> ⚠️ Change the admin password immediately in any production deployment.

---

## 🐳 Docker Compose (One-Command Start)

```bash
# Copy and configure env
cp backend/.env.example backend/.env
# Edit backend/.env with your keys

# Start everything
docker compose up --build
```

Services:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
trek management/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # JWT authentication
│   ├── routers/
│   │   ├── treks.py         # Trek CRUD + reviews
│   │   ├── bookings.py      # Booking management
│   │   ├── users.py         # User auth + profile
│   │   └── ai.py            # 7 AI-powered endpoints
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/           # React page components
│   │   ├── components/      # Reusable UI components
│   │   ├── store/           # Zustand state management
│   │   └── api/             # Axios API client
│   ├── package.json
│   ├── .env
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 📸 Screenshots

> _Coming soon — screenshots of the Trek Catalog, AI Chat, Difficulty Predictor, and Admin Dashboard._

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS, Framer Motion, Zustand, Axios |
| Backend | FastAPI, SQLAlchemy, Pydantic, python-jose, passlib |
| Database | SQLite (dev) / PostgreSQL-ready |
| AI | Google Gemini 1.5 Flash via google-generativeai |
| Auth | JWT Bearer tokens (24-hour expiry) |
| Container | Docker + Docker Compose |

---

## 📄 License

MIT License — feel free to fork and build on it!
