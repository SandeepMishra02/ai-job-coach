from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from routers import ai
from env.ratelimit import limiter, rate_limit_handler, SlowAPIMiddleware

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "").strip()
VERCEL_URL = os.getenv("VERCEL_URL", "").strip()           # e.g., https://ai-job-coach-eight.vercel.app
LOCAL_VITE = os.getenv("LOCAL_VITE", "http://localhost:5173").strip()

app = FastAPI(title="AI Job Coach", version="1.0.0")

# Attach limiter & middleware (app-wide)
app.state.limiter = limiter
app.add_exception_handler(type(rate_limit_handler.__args__[0]) if hasattr(rate_limit_handler, "__args__") else Exception, rate_limit_handler)  # runtime-safe
app.add_exception_handler(limiter.rate_limit_exceeded, rate_limit_handler)  # explicit
app.add_middleware(SlowAPIMiddleware)

# CORS
origins = {LOCAL_VITE}
if FRONTEND_URL:
    origins.add(FRONTEND_URL)
if VERCEL_URL:
    origins.add(VERCEL_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ai.router, prefix="", tags=["AI"])

@app.get("/health")
def health():
    return {"status": "ok"}



