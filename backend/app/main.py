"""
DreamScape web backend — FastAPI.

Two jobs:
1. POST /api/generate  -> runs the full free pipeline for one dream, returns video_url
2. GET  /api/journal    -> lists past generated dreams (reads each run's metadata.json)

Also serves the frontend (../frontend) and the generated videos (runs/) as static files.

Run locally:
    pip install fastapi uvicorn --break-system-packages
    uvicorn app:app --reload --port 8000
Then open http://localhost:8000
"""

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.pipeline import run_dreamscape_pipeline

RUNS_DIR = "runs"
FRONTEND_DIR = "../frontend"

os.makedirs(RUNS_DIR, exist_ok=True)

app = FastAPI(title="DreamScape")

# Needed because the frontend can be hosted separately (e.g. on Vercel) from
# this backend (e.g. on Render) — without this, the browser blocks the request.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a hackathon demo; narrow this to your Vercel URL later if you want
    allow_methods=["*"],
    allow_headers=["*"],
)


class DreamRequest(BaseModel):
    dream_text: str
    narration_enabled: bool = True


@app.post("/api/generate")
def generate_dream(req: DreamRequest):
    """Run the pipeline on submitted dream text and return the result once the video is ready.

    This blocks until the video is done (roughly 30-90s depending on scene count),
    which is fine for a hackathon demo — the frontend shows a loading state while it waits.
    """
    if not req.dream_text.strip():
        raise HTTPException(status_code=400, detail="Dream text is required")

    try:
        result = run_dreamscape_pipeline(
            req.dream_text,
            narration_enabled=req.narration_enabled,
            work_dir=RUNS_DIR,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    return result


@app.get("/api/journal")
def get_journal():
    """Return metadata for every past run, most recent first."""
    entries = []
    if os.path.isdir(RUNS_DIR):
        for run_id in os.listdir(RUNS_DIR):
            meta_path = os.path.join(RUNS_DIR, run_id, "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    entries.append(json.load(f))

    entries.sort(key=lambda e: e["created_at"], reverse=True)
    return entries


# Order matters: API routes above are matched first, then generated videos,
# then the frontend catch-all last (so it doesn't swallow /api or /runs requests).
app.mount("/runs", StaticFiles(directory=RUNS_DIR), name="runs")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
