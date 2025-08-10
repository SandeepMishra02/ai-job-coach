# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ✅ relative import from the same package
from .routers import ai

load_dotenv()

app = FastAPI()

# CORS: your deployed Vercel URL + local dev
ALLOWED_ORIGINS = [
    "https://ai-job-coach-eight.vercel.app",  # change if your Vercel URL differs
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API router
app.include_router(ai.router)





