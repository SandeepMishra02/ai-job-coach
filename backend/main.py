from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-job-coach-eight.vercel.app",  
        "http://localhost:5173"  # local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router)


