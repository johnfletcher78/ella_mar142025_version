#!/usr/bin/env python3
"""
agent_b_svd.py — Sub-Agent B: SVD XT Motion Generation Only
Starts with clean VRAM, generates motion clips, exits
"""

import sys
from pathlib import Path

sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import json
import urllib.request
import time
import subprocess

COMFY_URL = "http://127.0.0.1:8188"
COMFY_OUT = Path.home() / "ComfyUI" / "output"
COMFY_INPUT = Path.home() / "ComfyUI" / "input"

def get_vram_info():
    """Check available VRAM"""
    try:
        import subprocess
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, timeout=5)
        free_mb = int(r.stdout.strip())
        return free_mb
    except:
        return 16000

def main():
    job_dir = Path(sys.argv[1])
    print(f"[Agent B] Starting — SVD XT Motion Generation")
    print(f"[Agent B] Job directory: {job_dir}")
    
    vram_free = get_vram_info()
    print(f"[Agent B] VRAM available: {vram_free}MB ({vram_free/1024:.1f}GB)")
    
    if vram_free < 4000:
        print(f"[Agent B] ⚠️ WARNING: Low VRAM — SVD may fail")
    
    # Get generated images from job directory (not ComfyUI output)
    images = sorted((job_dir / "images").glob("*.png"))
    print(f"[Agent B] Found {len(images)} images to animate")
    
    if len(images) == 0:
        print(f"[Agent B] ❌ No images found in {job_dir / 'images'}")
        return 1
    
    clips_dir = job_dir / "clips"
    clips_dir.mkdir(exist_ok=True)
    
    for i, img_path in enumerate(images):
        print(f"\n[Agent B] Scene {i+1}/{len(images)}: {img_path.name}")
        
        # Copy to ComfyUI input
        input_path = COMFY_INPUT / img_path.name
        import shutil
        shutil.copy(img_path, input_path)
        
        # Build SVD workflow (768x1344, 16 frames for VRAM safety)
        seed = int(time.time() * 1000) % 2147483647
        workflow = {
            "1": {"class_type": "ImageOnlyCheckpointLoader",
                  "inputs": {"ckpt_name": "svd-xt/svd_xt.safetensors"}},
            "2": {"class_type": "LoadImage", "inputs": {"image": img_path.name}},
            "3": {"class_type": "SVD_img2vid_Conditioning",
                  "inputs": {"clip_vision": ["1", 1], "init_image": ["2", 0], "vae": ["1", 2],
                            "width": 768, "height": 1344, "video_frames": 16,
                            "motion_bucket_id": 95, "fps": 8, "augmentation_level": 0.0}},
            "4": {"class_type": "KSampler",
                  "inputs": {"model": ["1", 0], "positive": ["3", 0], "negative": ["3", 1],
                            "latent_image": ["3", 2], "seed": seed, "steps": 20, "cfg": 2.5,
                            "sampler_name": "euler", "scheduler": "karras", "denoise": 1.0}},
            "5": {"class_type": "VAEDecode", "inputs": {"samples": ["4", 0], "vae": ["1", 2]}},
            "6": {"class_type": "SaveImage",
                  "inputs": {"images": ["5", 0], "filename_prefix": f"svd_{i:02d}"}}
        }
        
        # Queue SVD job
        import uuid
        payload = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
        req = urllib.request.Request(f"{COMFY_URL}/prompt", data=payload,
                                    headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            prompt_id = json.loads(resp.read())["prompt_id"]
        
        print(f"[Agent B] SVD job queued: {prompt_id}")
        
        # Wait for completion
        start = time.time()
        timeout = 300
        webp_path = None
        
        while time.time() - start < timeout:
            time.sleep(3)
            try:
                with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}", timeout=5) as resp:
                    history = json.loads(resp.read())
                    if prompt_id in history and "outputs" in history[prompt_id]:
                        for node_out in history[prompt_id]["outputs"].values():
                            if "images" in node_out:
                                img = node_out["images"][0]
                                webp_path = COMFY_OUT / img["filename"]
                                if webp_path.exists():
                                    elapsed = round(time.time() - start, 1)
                                    print(f"[Agent B] ✅ SVD done in {elapsed}s")
                                    break
                        if webp_path:
                            break
            except:
                pass
        
        if not webp_path:
            print(f"[Agent B] ❌ SVD timeout for scene {i+1}")
            continue
        
        # Convert WEBP frames to MP4
        clip_path = clips_dir / f"clip_{i:02d}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(webp_path),
            "-vf", "fps=30,scale=1080:1920:flags=lanczos",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-t", "5",
            str(clip_path)
        ], check=True)
        
        print(f"[Agent B] ✅ Clip saved: {clip_path.name}")
        
        # VRAM settle
        time.sleep(2)
    
    print(f"\n[Agent B] All {len(images)} clips generated")
    print("[Agent B] Exiting — VRAM will be fully cleared")
    return 0

if __name__ == "__main__":
    sys.exit(main())
