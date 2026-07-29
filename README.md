# DreamScape

Text-to-dream-film generator. 100% free stack: no API keys, no signup, no billing anywhere.

## Project layout

```
dreamscape-webapp/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app: routes + static file serving
│   │   ├── pipeline.py          orchestrates the 4 steps below, saves journal metadata
│   │   └── services/
│   │       ├── scene_breakdown.py   free LLM (Pollinations text) — dream text -> scenes
│   │       ├── image_gen.py         free image gen (Pollinations image) — scene -> still
│   │       ├── narration_tts.py     free narration (edge-tts) — scene -> voice line
│   │       └── video_stitch.py      moviepy/ffmpeg — stills + audio -> final mp4
│   ├── assets/ambient/           drop your royalty-free mood tracks here (not included)
│   ├── runs/                     created automatically, one folder per generated dream
│   └── requirements.txt
├── frontend/
│   └── index.html                single page, no build step
├── Dockerfile                    used for Render (or any Docker host) deployment
├── render.yaml                   Render Blueprint for one-click deploy
└── .gitignore
```

## Run locally (recommended for demo day)

```
cd backend
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload --port 8000
```
Install ffmpeg separately if you don't have it: `brew install ffmpeg` (Mac) or `sudo apt install ffmpeg` (Ubuntu).
Open **http://localhost:8000** — not the index.html file directly, it needs the server behind it.

## Add ambient audio (optional)

Drop royalty-free mp3s into `backend/assets/ambient/`, named to match the mood tags:
`calm.mp3, unsettling.mp3, chaotic.mp3, nostalgic.mp3, eerie.mp3, joyful.mp3`
(Free sources: Pixabay Audio, Freesound.org). Missing files are skipped silently, not required to run.

## Deploy for free (public link)

**Render.com** — no credit card needed for the free Hobby tier:
1. Push this folder to a GitHub repo.
2. On Render: New + → Blueprint → connect the repo. It reads `render.yaml` automatically.
   (Or: New + → Web Service → connect repo → Environment: Docker → it finds the Dockerfile.)
3. First deploy takes a few minutes (installs ffmpeg + deps inside the container).
4. Your app gets a `*.onrender.com` URL. Free tier spins down after 15 min idle —
   visit it a minute or two before your demo so it's already warm.

Local Docker test before deploying (optional, needs Docker installed):
```
docker build -t dreamscape .
docker run -p 8000:8000 dreamscape
```

## How the pipeline connects

`app/main.py` → `app/pipeline.py` → calls each `app/services/*.py` in order → writes
`backend/runs/<run_id>/metadata.json` → `/api/journal` reads all of those to populate
the Dream Journal section on the page.
