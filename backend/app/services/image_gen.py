"""
Image generation step for DreamScape — FREE version (Pollinations.ai, no API key).

Takes scenes from scene_breakdown.py (each already has "image_gen_prompt")
and generates one image per scene using Pollinations' free image endpoint.
No signup, no key, no billing — a single GET request returns the image bytes directly.

Usage:
    from image_gen import generate_scene_images
    scenes = generate_scene_images(scenes, output_dir="assets")
"""

import os
import urllib.parse
import requests

IMAGE_API_BASE = "https://image.pollinations.ai/prompt"


def _generate_single_image(prompt: str, width: int = 1024, height: int = 576, seed: int | None = None) -> bytes:
    """Request one image from Pollinations and return the raw image bytes."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{IMAGE_API_BASE}/{encoded_prompt}"

    params = {
        "width": width,
        "height": height,
        "nologo": "true",   # hides the pollinations watermark
    }
    if seed is not None:
        params["seed"] = seed  # fix a seed if you want reproducible results across runs

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.content


def generate_scene_images(scenes: list[dict], output_dir: str = "assets") -> list[dict]:
    """Generate one image per scene, save it locally, and attach image_path to each scene dict."""
    os.makedirs(output_dir, exist_ok=True)

    for scene in scenes:
        image_bytes = _generate_single_image(scene["image_gen_prompt"], seed=scene.get("order"))

        image_path = os.path.join(output_dir, f"scene_{scene['order']}.png")
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        scene["image_path"] = image_path

    return scenes


if __name__ == "__main__":
    demo_scenes = [
        {"order": 1, "image_gen_prompt": "falling through clouds, dreamlike, surreal, soft focus, muted colors, illustrated, cinematic lighting"},
    ]
    result = generate_scene_images(demo_scenes)
    print(result)
