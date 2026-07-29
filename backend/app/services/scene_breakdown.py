"""
Scene breakdown step for DreamScape — FREE version (Pollinations.ai, no API key).

Takes messy/fragmented dream text and turns it into 3-5 structured scenes,
each with a visual prompt (ready to feed straight into the image model)
and a mood tag (used to pick ambient audio).

No signup, no key, no billing. Pollinations' free text endpoint proxies
several models (default "openai") at no cost.

Usage:
    from scene_breakdown import break_dream_into_scenes
    scenes = break_dream_into_scenes("I was falling, there was a red door, my teeth were falling out")
"""

import json
import requests

TEXT_API_URL = "https://text.pollinations.ai/openai"

# Pin this suffix onto every scene's visual prompt so all scenes share one art style
# instead of looking like five random images.
STYLE_SUFFIX = "dreamlike, surreal, soft focus, muted colors, illustrated, cinematic lighting"

# Only these mood tags exist -> must match your curated ambient audio library exactly.
VALID_MOODS = ["calm", "unsettling", "chaotic", "nostalgic", "eerie", "joyful"]

SYSTEM_PROMPT = f"""You are a dream interpreter for a text-to-dream-film generator.

Given raw, possibly fragmented or non-linear dream text from a user, break it into
3 to 5 distinct visual scenes that could be storyboarded and illustrated.

Rules:
- Each scene needs a vivid, concrete visual description (what's on screen), not an
  interpretation of what the dream "means."
- Keep descriptions specific enough for a text-to-image model to render consistently
  (concrete nouns, setting, lighting, key objects/figures) but under 40 words.
- Assign exactly one mood tag per scene from this fixed list: {", ".join(VALID_MOODS)}.
- Order scenes to match the sequence implied by the input, or a natural dream arc
  if the input is non-linear.
- Give each scene a short duration_seconds value (6-12) based on how much is
  happening in it, summing to roughly 30-60 seconds total.
- Write a one-sentence narration_line per scene, phrased like a soft dream narrator
  describing it in the moment (present tense, second person e.g. "You are...").

Respond with ONLY valid JSON, no preamble, no markdown fences, matching this schema:
{{
  "scenes": [
    {{
      "order": 1,
      "visual_prompt": "string",
      "mood": "one of the fixed mood tags",
      "duration_seconds": 8,
      "narration_line": "string"
    }}
  ]
}}
"""


def break_dream_into_scenes(dream_text: str, model: str = "openai") -> list[dict]:
    """Call Pollinations' free text API to turn raw dream text into structured scenes."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": dream_text},
        ],
        "temperature": 0.8,
        "max_tokens": 1500,
    }

    response = requests.post(TEXT_API_URL, json=payload, timeout=60)
    response.raise_for_status()
    raw_text = response.json()["choices"][0]["message"]["content"].strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw output:\n{raw_text}")

    scenes = parsed.get("scenes", [])
    if not (3 <= len(scenes) <= 5):
        raise ValueError(f"Expected 3-5 scenes, got {len(scenes)}")

    for scene in scenes:
        if scene["mood"] not in VALID_MOODS:
            raise ValueError(f"Invalid mood '{scene['mood']}' — not in {VALID_MOODS}")
        scene["image_gen_prompt"] = f"{scene['visual_prompt']}, {STYLE_SUFFIX}"

    return scenes


if __name__ == "__main__":
    example = "I was falling, there was a red door, my teeth were falling out"
    scenes = break_dream_into_scenes(example)
    print(json.dumps(scenes, indent=2))
