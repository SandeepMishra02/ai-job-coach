from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from routers import ai
from backend.rate_limit import limiter, rate_limit_handler, SlowAPIMiddleware

app = FastAPI(title="AI Job Coach", version="1.0.0")

# CORS
ALLOWED_ORIGINS = [
    "https://ai-job-coach-eight.vercel.app",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SlowAPI (global)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

from slowapi.errors import RateLimitExceeded
@app.exception_handler(RateLimitExceeded)
async def _rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
    return rate_limit_handler(request, exc)

# Routes
app.include_router(ai.router)

@app.get("/health")
def health():
    return {"status": "ok"}




