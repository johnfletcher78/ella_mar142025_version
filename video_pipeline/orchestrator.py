#!/usr/bin/env python3
"""
orchestrator.py — Traffic controller for video pipeline
One sub-agent → One model → Exit → Clean VRAM
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / ".openclaw/workspace/video_jobs"

def run_video_job(scene_prompts: list, job_id: str = None):
    """Orchestrate the full pipeline via sub-agents"""
    
    if job_id is None:
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    job_dir = BASE_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (job_dir / "images").mkdir(exist_ok=True)
    (job_dir / "clips").mkdir(exist_ok=True)
    (job_dir / "output").mkdir(exist_ok=True)
    
    print(f"🎬 Video Job: {job_id}")
    print(f"📁 Directory: {job_dir}")
    print(f"📝 Scenes: {len(scene_prompts)}")
    print("=" * 50)
    
    # Write prompts for Sub-Agent A
    prompts_file = job_dir / "prompts.json"
    with open(prompts_file, "w") as f:
        json.dump(scene_prompts, f, indent=2)
    
    # Launch Sub-Agent A: SDXL Image Generation
    print("\n🚀 Sub-Agent A: SDXL Image Generation")
    print("   Loading Juggernaut XL v9...")
    result_a = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "agent_a_sdxl.py"), str(job_dir)],
        capture_output=True,
        text=True
    )
    print(result_a.stdout)
    if result_a.returncode != 0:
        print(f"❌ Sub-Agent A failed: {result_a.stderr}")
        return None
    
    # Launch Sub-Agent B: SVD Motion Generation  
    print("\n🚀 Sub-Agent B: SVD XT Motion Generation")
    print("   Loading Stable Video Diffusion XT...")
    result_b = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "agent_b_svd.py"), str(job_dir)],
        capture_output=True,
        text=True
    )
    print(result_b.stdout)
    if result_b.returncode != 0:
        print(f"❌ Sub-Agent B failed: {result_b.stderr}")
        return None
    
    # Launch Sub-Agent C: FFmpeg Assembly
    print("\n🚀 Sub-Agent C: FFmpeg Assembly")
    print("   Assembling final video...")
    result_c = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "agent_c_ffmpeg.py"), str(job_dir)],
        capture_output=True,
        text=True
    )
    print(result_c.stdout)
    if result_c.returncode != 0:
        print(f"❌ Sub-Agent C failed: {result_c.stderr}")
        return None
    
    # Verify output
    final_video = job_dir / "output" / "final.mp4"
    if final_video.exists():
        size_mb = round(final_video.stat().st_size / 1024 / 1024, 1)
        print(f"\n✅ Job {job_id} complete!")
        print(f"📹 Final video: {final_video}")
        print(f"📊 Size: {size_mb}MB")
        return str(final_video)
    else:
        print(f"\n❌ Final video not found")
        return None

if __name__ == "__main__":
    # Example: Beer commercial
    prompts = [
        "ice cold craft beer bottle on wooden bar, condensation, golden sunset, product photography, vertical 9:16",
        "outdoor patio bar scene at golden hour, string lights, warm atmosphere, no people, vertical 9:16",
        "three hands clinking beer bottles in toast, outdoor summer, golden hour, close up, vertical 9:16"
    ]
    
    result = run_video_job(prompts)
    if result:
        print(f"\n🍺 Success! Video at: {result}")
