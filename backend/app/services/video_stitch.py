"""
Video stitching step for DreamScape (moviepy 2.x API).

Takes the scene list from scene_breakdown.py (after each scene has had its
image generated and, optionally, narration audio synthesized) and produces
one stitched video: Ken Burns pan/zoom per scene, ambient audio bed,
optional narration on top, crossfade transitions between scenes.

Expects each scene dict to already have:
    scene["image_path"]       -> path to generated still (from image-gen step)
    scene["duration_seconds"] -> from scene_breakdown
    scene["mood"]             -> from scene_breakdown
    scene["narration_path"]   -> path to TTS audio, or None if narration is off

Usage:
    from video_stitch import stitch_dream_video
    stitch_dream_video(scenes, output_path="dream.mp4")
"""

import random
from moviepy import (
    ImageClip,
    CompositeAudioClip,
    AudioFileClip,
    concatenate_videoclips,
)
from moviepy.video.fx import CrossFadeIn, CrossFadeOut

# Map each mood tag (from scene_breakdown.py) to an ambient track in your curated library.
# Swap these paths for your actual royalty-free files.
AMBIENT_LIBRARY = {
    "calm": "assets/ambient/calm.mp3",
    "unsettling": "assets/ambient/unsettling.mp3",
    "chaotic": "assets/ambient/chaotic.mp3",
    "nostalgic": "assets/ambient/nostalgic.mp3",
    "eerie": "assets/ambient/eerie.mp3",
    "joyful": "assets/ambient/joyful.mp3",
}

CROSSFADE_SECONDS = 1.0
ZOOM_RANGE = (1.0, 1.15)  # start/end scale for the Ken Burns zoom


def _ken_burns_clip(image_path: str, duration: float) -> ImageClip:
    """Animate a still image with a slow pan+zoom (Ken Burns effect)."""
    clip = ImageClip(image_path).with_duration(duration)

    zoom_start, zoom_end = ZOOM_RANGE
    # Randomize direction a bit so scenes don't all zoom identically
    if random.random() < 0.5:
        zoom_start, zoom_end = zoom_end, zoom_start

    def zoom(t):
        progress = t / duration
        return zoom_start + (zoom_end - zoom_start) * progress

    animated = clip.resized(zoom)
    # Recentre after resize so the zoom pulls toward the middle rather than drifting
    animated = animated.with_position(("center", "center"))
    return animated


def _scene_audio(scene: dict, duration: float):
    """Build this scene's audio: ambient bed, optionally layered with narration."""
    ambient_path = AMBIENT_LIBRARY.get(scene["mood"])
    tracks = []

    if ambient_path:
        try:
            ambient = AudioFileClip(ambient_path).subclipped(0, duration).with_volume_scaled(0.4)
            tracks.append(ambient)
        except (IOError, OSError):
            pass  # ambient file not present yet — skip rather than crash the whole run

    if scene.get("narration_path"):
        narration = AudioFileClip(scene["narration_path"]).with_volume_scaled(1.0)
        tracks.append(narration)

    if not tracks:
        return None
    return CompositeAudioClip(tracks).with_duration(duration)


def stitch_dream_video(scenes: list[dict], output_path: str = "dream.mp4", fps: int = 24) -> str:
    """Build the final dream video from a list of scene dicts and write it to output_path."""
    clips = []

    for scene in scenes:
        duration = scene["duration_seconds"]
        visual = _ken_burns_clip(scene["image_path"], duration)

        audio = _scene_audio(scene, duration)
        if audio is not None:
            visual = visual.with_audio(audio)

        # Crossfade in/out so cuts between scenes feel dreamlike, not hard-cut
        visual = visual.with_effects([CrossFadeIn(CROSSFADE_SECONDS), CrossFadeOut(CROSSFADE_SECONDS)])
        clips.append(visual)

    final = concatenate_videoclips(clips, method="compose", padding=-CROSSFADE_SECONDS)
    final.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac")
    return output_path


if __name__ == "__main__":
    # Minimal smoke-test shape — replace with real paths from your pipeline
    demo_scenes = [
        {
            "image_path": "assets/scene1.png",
            "duration_seconds": 8,
            "mood": "unsettling",
            "narration_path": None,
        },
        {
            "image_path": "assets/scene2.png",
            "duration_seconds": 10,
            "mood": "eerie",
            "narration_path": None,
        },
    ]
    stitch_dream_video(demo_scenes, output_path="dream_demo.mp4")
