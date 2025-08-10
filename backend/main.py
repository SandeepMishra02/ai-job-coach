from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import routers
from routers import ai

load_dotenv()

app = FastAPI(title="AI Job Coach API")

# CORS: configure via env, fallback to sensible defaults
# Example env: ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if allowed_origins_env:
    origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    # Fallback for local + your current Vercel app
    origins = [
        "http://localhost:5173",
        "https://ai-job-coach-eight.vercel.app"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health/root endpoints for sanity checks
@app.get("/")
def root():
    return {"message": "Backend is running", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"ok": True}

# Mount feature routers
app.include_router(ai.router)



