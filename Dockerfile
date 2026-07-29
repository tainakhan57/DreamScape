# DreamScape — single container running the FastAPI backend + serving the frontend.
# Free-tier friendly: small base image, only ffmpeg added on top.

FROM python:3.11-slim

# ffmpeg is required by moviepy for video stitching
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/ /app/frontend/

# Render (and most free hosts) inject $PORT at runtime; default to 8000 for local docker run
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
