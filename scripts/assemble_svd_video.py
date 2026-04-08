#!/usr/bin/env python3
"""Assemble SVD frames into final video"""

import subprocess
from pathlib import Path

OUTPUT_DIR = Path.home() / "ComfyUI" / "output"
FINAL_OUTPUT = Path.home() / ".openclaw/workspace/output/beer_svd_final.mp4"

# Create video from SVD frame sequences
scenes = [
    ("svd_01_*.png", "scene1.mp4"),
    ("svd_02_*.png", "scene2.mp4"),
    ("svd_03_*.png", "scene3.mp4")
]

clip_paths = []

for pattern, output in scenes:
    # Get sorted list of frames
    frames = sorted(OUTPUT_DIR.glob(pattern))
    if not frames:
        print(f"No frames for {pattern}")
        continue
    
    # Create file list for ffmpeg
    list_file = OUTPUT_DIR / f"{output}_list.txt"
    with open(list_file, "w") as f:
        for frame in frames:
            f.write(f"file '{frame}'\n")
            f.write(f"duration 0.125\n")  # 8fps = 0.125s per frame
    
    # Convert frames to video
    output_path = OUTPUT_DIR / output
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-vf", "fps=30,scale=1080:1920:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-t", "5",  # 5 seconds per scene
        str(output_path)
    ], check=True)
    
    list_file.unlink()
    clip_paths.append(output_path)
    print(f"✅ {output}: {len(frames)} frames")

# Concatenate all scenes
concat_file = OUTPUT_DIR / "final_concat.txt"
with open(concat_file, "w") as f:
    for clip in clip_paths:
        f.write(f"file '{clip}'\n")
        f.write(f"duration 5\n")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-f", "concat", "-safe", "0",
    "-i", str(concat_file),
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-movflags", "+faststart",
    str(FINAL_OUTPUT)
], check=True)

concat_file.unlink()

# Cleanup temp clips
for clip in clip_paths:
    clip.unlink()

print(f"\n🍺 TRUE AI MOTION VIDEO COMPLETE!")
print(f"Output: {FINAL_OUTPUT}")
print(f"Resolution: 1080x1920")
print(f"Duration: 15 seconds (3 scenes × 5s)")
print(f"Motion: REAL SVD animation (not Ken Burns!)")
