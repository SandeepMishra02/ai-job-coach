# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routers import ai
from .routers import applications
from .routers import analytics
from .routers import interview
from .db import init_db

load_dotenv()
init_db()

app = FastAPI(title="AI Job Coach API")

ALLOWED_ORIGINS = [
    "https://ai-job-coach-eight.vercel.app",  # <-- your Vercel frontend
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ai.router)
app.include_router(applications.router)
app.include_router(analytics.router)
app.include_router(interview.router)
