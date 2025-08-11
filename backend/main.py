from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routers import ai, applications, analytics, interview
from .db import init_db

load_dotenv()
init_db()

app = FastAPI(title="AI Job Coach API")

# Allow your fixed prod domain AND any Vercel preview domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-job-coach-eight.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],  # includes OPTIONS
    allow_headers=["*"],
)

# Routers
app.include_router(ai.router)
app.include_router(applications.router)
app.include_router(analytics.router)
app.include_router(interview.router)

