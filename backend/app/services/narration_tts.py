"""
Narration step for DreamScape — FREE version (edge-tts, no API key).

Takes scenes from scene_breakdown.py (each already has "narration_line")
and synthesizes a soft, dreamy voiceover per scene using edge-tts, a free
Python wrapper around Microsoft Edge's neural text-to-speech voices.
No signup, no key, no billing, runs locally against a free public endpoint.

Install: pip install edge-tts --break-system-packages

Usage:
    from narration_tts import generate_scene_narration
    scenes = generate_scene_narration(scenes, output_dir="assets")
"""

import asyncio
import os
import edge_tts

# A soft, calm-sounding neural voice. Run `edge-tts --list-voices` to see 200+ others.
VOICE = "en-US-JennyNeural"


async def _synthesize(text: str, output_path: str) -> None:
    """Send one line of narration text to edge-tts and save the mp3."""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)


def generate_scene_narration(scenes: list[dict], output_dir: str = "assets", enabled: bool = True) -> list[dict]:
    """Synthesize narration audio per scene and attach narration_path to each scene dict.

    Set enabled=False to skip narration entirely (video_stitch.py already handles
    narration_path being None).
    """
    os.makedirs(output_dir, exist_ok=True)

    for scene in scenes:
        if not enabled or not scene.get("narration_line"):
            scene["narration_path"] = None
            continue

        narration_path = os.path.join(output_dir, f"narration_{scene['order']}.mp3")
        asyncio.run(_synthesize(scene["narration_line"], narration_path))
        scene["narration_path"] = narration_path

    return scenes


if __name__ == "__main__":
    demo_scenes = [
        {"order": 1, "narration_line": "You are falling through endless grey clouds."},
    ]
    result = generate_scene_narration(demo_scenes)
    print(result)
