"""
DreamScape pipeline orchestrator — FREE version, no API keys required anywhere.

Ties every step together: raw dream text -> structured scenes (Pollinations text)
-> AI images (Pollinations image) -> AI narration (edge-tts) -> stitched video.
Saves a metadata.json per run so the web app can list past dreams (the "dream journal").

Usage:
    from pipeline import run_dreamscape_pipeline
    result = run_dreamscape_pipeline("I was falling, there was a red door")
"""

import json
import os
import uuid
from datetime import datetime, timezone

from app.services.scene_breakdown import break_dream_into_scenes
from app.services.image_gen import generate_scene_images
from app.services.narration_tts import generate_scene_narration
from app.services.video_stitch import stitch_dream_video


def run_dreamscape_pipeline(dream_text: str, narration_enabled: bool = True, work_dir: str = "runs") -> dict:
    """Run the full pipeline for one dream and return a dict describing the result.

    Each run gets its own subfolder (named by run_id) under work_dir, so past runs
    never overwrite each other's assets — this is what powers the dream journal.
    """
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:6]
    run_dir = os.path.join(work_dir, run_id)
    os.makedirs(run_dir, exist_ok=True)

    print(f"[{run_id}] breaking dream into scenes...")
    scenes = break_dream_into_scenes(dream_text)

    print(f"[{run_id}] generating {len(scenes)} images...")
    scenes = generate_scene_images(scenes, output_dir=run_dir)

    print(f"[{run_id}] generating narration...")
    scenes = generate_scene_narration(scenes, output_dir=run_dir, enabled=narration_enabled)

    print(f"[{run_id}] stitching final video...")
    video_filename = "dream.mp4"
    output_path = os.path.join(run_dir, video_filename)
    stitch_dream_video(scenes, output_path=output_path)

    result = {
        "run_id": run_id,
        "dream_text": dream_text,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "video_url": f"/runs/{run_id}/{video_filename}",
        "scene_count": len(scenes),
        "moods": [s["mood"] for s in scenes],
    }

    with open(os.path.join(run_dir, "metadata.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"[{run_id}] done -> {output_path}")
    return result


if __name__ == "__main__":
    dream = input("Describe your dream: ")
    result = run_dreamscape_pipeline(dream)
    print(f"\nYour dream film is ready: {result['video_url']}")
