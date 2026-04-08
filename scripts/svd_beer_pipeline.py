#!/usr/bin/env python3
"""Animate 3 beer images with SVD XT and assemble final video"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import json
import urllib.request
import subprocess
import shutil
from pathlib import Path
import time

COMFY_URL = "http://127.0.0.1:8188"
COMFY_OUT = Path.home() / "ComfyUI" / "output"
COMFY_INPUT = Path.home() / "ComfyUI" / "input"
OUTPUT_DIR = Path.home() / "videos" / "shorts"

# Images to animate
images = [
    "scene_01_friends_patio_00001_.png",
    "scene_02_money_shot_00001_.png", 
    "scene_03_group_toast_00001_.png"
]

def get_vram():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], 
                          capture_output=True, text=True, timeout=5)
        return int(r.stdout.strip())
    except:
        return 16000

def check_vram():
    free = get_vram()
    print(f"[vram] Free: {free}MiB")
    if free < 2000:
        print("[vram] WARNING: Low VRAM")
        return False
    return True

def comfy_interrupt():
    try:
        req = urllib.request.Request(f"{COMFY_URL}/interrupt", data=b"{}", method="POST")
        urllib.request.urlopen(req, timeout=5)
        time.sleep(5)
        print("[vram] Interrupt sent, VRAM settled")
    except Exception as e:
        print(f"[vram] Interrupt: {e}")

def build_svd_workflow(image_name, seed=-1):
    """SVD XT workflow for image-to-video"""
    if seed == -1:
        seed = int(time.time() * 1000) % 2147483647
    
    return {
        "1": {
            "class_type": "ImageOnlyCheckpointLoader",
            "inputs": {"ckpt_name": "svd-xt/svd_xt.safetensors"}
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {"image": image_name}
        },
        "3": {
            "class_type": "SVD_img2vid_Conditioning",
            "inputs": {
                "clip_vision": ["1", 1],
                "init_image": ["2", 0],
                "vae": ["1", 2],
                "width": 1080,
                "height": 1920,
                "video_frames": 25,  # 5 seconds at 5fps
                "motion_bucket_id": 95,  # moderate motion per Claude
                "fps": 8,
                "augmentation_level": 0.0
            }
        },
        "4": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["3", 0],
                "negative": ["3", 1],
                "latent_image": ["3", 2],
                "seed": seed,
                "steps": 20,  # SVD quality/speed balance
                "cfg": 2.5,   # SVD uses low CFG
                "sampler_name": "euler",
                "scheduler": "karras",
                "denoise": 1.0
            }
        },
        "5": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["4", 0], "vae": ["1", 2]}
        },
        "6": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["5", 0],
                "filename_prefix": "svd_beer",
                "fps": 8,
                "lossless": False,
                "quality": 90
            }
        }
    }

def queue_and_wait(workflow, timeout=300):
    import uuid
    payload = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=payload,
                                headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        prompt_id = json.loads(resp.read())["prompt_id"]
    
    print(f"  SVD job queued: {prompt_id}")
    start = time.time()
    
    while time.time() - start < timeout:
        time.sleep(3)
        try:
            with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}", timeout=5) as resp:
                history = json.loads(resp.read())
                if prompt_id in history and "outputs" in history[prompt_id]:
                    for node_out in history[prompt_id]["outputs"].values():
                        if "animated" in node_out:
                            anim = node_out["animated"][0]
                            path = COMFY_OUT / anim["filename"]
                            if path.exists():
                                elapsed = round(time.time() - start, 1)
                                print(f"  ✅ SVD done in {elapsed}s: {path.name}")
                                return path
        except:
            pass
    raise TimeoutError("SVD timeout")

def convert_webp_to_mp4(webp_path, output_path, duration=5):
    """Convert SVD WEBP to MP4 at 30fps"""
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(webp_path),
        "-vf", "scale=1080:1920:flags=lanczos,fps=30",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),
        str(output_path)
    ], check=True)
    mb = round(output_path.stat().st_size / 1024 / 1024, 1)
    print(f"  Converted: {output_path.name} ({mb}MB)")
    return output_path

def assemble_final(clips, output):
    """Concatenate clips into final video"""
    concat_file = output.parent / "concat.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.absolute()}'\n")
            f.write(f"duration 5\n")
    
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output)
    ], check=True)
    
    concat_file.unlink(missing_ok=True)
    mb = round(output.stat().st_size / 1024 / 1024, 1)
    print(f"✅ Final video: {output.name} ({mb}MB)")
    return output

# Main pipeline
print("🎬 SVD XT Beer Commercial Pipeline")
print("=" * 50)

if not check_vram():
    print("Low VRAM warning — continuing anyway")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
job_id = f"beer_svd_{int(time.time())}"
job_dir = OUTPUT_DIR / job_id
job_dir.mkdir(exist_ok=True)

# Animate each image with SVD
print("\n🎥 Animating 3 images with Stable Video Diffusion XT...")
print("  (This takes ~45-60s per clip)\n")

clips = []
for i, img_name in enumerate(images, 1):
    print(f"Scene {i}: {img_name}")
    
    # Copy image to ComfyUI input
    src = COMFY_OUT / img_name
    dst = COMFY_INPUT / img_name
    shutil.copy(src, dst)
    
    # Run SVD
    wf = build_svd_workflow(img_name)
    webp = queue_and_wait(wf)
    
    # Convert to MP4
    mp4 = job_dir / f"clip_{i:02d}.mp4"
    convert_webp_to_mp4(webp, mp4)
    clips.append(mp4)
    
    # VRAM management
    comfy_interrupt()

# Assemble final
print("\n🔧 Assembling final video...")
final = job_dir / f"{job_id}_final.mp4"
assemble_final(clips, final)

print(f"\n🍺 Beer commercial complete!")
print(f"Output: {final}")
