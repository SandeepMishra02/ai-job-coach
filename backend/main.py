from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv

from routers import ai, applications, analytics, interview, jobs
from db import init_db

load_dotenv()
init_db()

app = FastAPI(title="AI Job Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-job-coach-eight.vercel.app",  # your prod frontend
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app$",  # allow all Vercel previews
    allow_credentials=True,   # keep False unless you're doing cookie auth
    allow_methods=["*"],
    allow_headers=["*"],
)



# Routers
app.include_router(ai.router)
app.include_router(applications.router)
app.include_router(analytics.router)
app.include_router(interview.router)
app.include_router(jobs.router)

