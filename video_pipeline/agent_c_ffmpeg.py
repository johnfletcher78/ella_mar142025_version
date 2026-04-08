#!/usr/bin/env python3
"""
agent_c_ffmpeg.py — Sub-Agent C: FFmpeg Assembly Only
Pure CPU — no GPU. Assembles clips into final video.
"""

import sys
import subprocess
from pathlib import Path

def main():
    job_dir = Path(sys.argv[1])
    print(f"[Agent C] Starting — FFmpeg Assembly")
    print(f"[Agent C] Job directory: {job_dir}")
    
    # Get all clips
    clips = sorted((job_dir / "clips").glob("*.mp4"))
    print(f"[Agent C] Found {len(clips)} clips to assemble")
    
    output_dir = job_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Build FFmpeg concat list
    concat_file = job_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip}'\n")
            f.write(f"duration 5\n")  # Each clip is 5 seconds
    
    final_video = output_dir / "final.mp4"
    
    print(f"[Agent C] Assembling {len(clips)} clips into final video...")
    
    # Assemble with FFmpeg
    result = subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(final_video)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[Agent C] ❌ FFmpeg failed: {result.stderr}")
        return 1
    
    # Cleanup
    concat_file.unlink()
    
    # Report
    size_mb = round(final_video.stat().st_size / 1024 / 1024, 1)
    print(f"[Agent C] ✅ Final video: {final_video.name}")
    print(f"[Agent C] 📊 Size: {size_mb}MB")
    print(f"[Agent C] 📹 Duration: {len(clips) * 5}s")
    print("[Agent C] Exiting — no VRAM used (CPU only)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
