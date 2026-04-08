#!/usr/bin/env python3
"""SVD XT workflow with properly loaded nodes"""

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

# Juggernaut XL images to animate
images = [
    "jug_scene_01_hero_00001_.png",
    "jug_scene_02_atmosphere_00001_.png",
    "jug_scene_03_hands_00001_.png"
]

def build_svd_workflow(image_name):
    """SVD XT workflow using proper ComfyUI nodes"""
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
                "video_frames": 25,
                "motion_bucket_id": 95,
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
                "steps": 20,
                "cfg": 2.5,
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
            "class_type": "SaveImage",
            "inputs": {"images": ["5", 0], "filename_prefix": f"svd_{image_name.split('_')[2]}"}
        }
    }

def queue_and_wait(workflow, timeout=300):
    import uuid
    payload = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=payload,
                                headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        prompt_id = json.loads(resp.read())["prompt_id"]
    
    print(f"  SVD job: {prompt_id}")
    start = time.time()
    
    while time.time() - start < timeout:
        time.sleep(3)
        try:
            with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}", timeout=5) as resp:
                history = json.loads(resp.read())
                if prompt_id in history and "outputs" in history[prompt_id]:
                    for node_out in history[prompt_id]["outputs"].values():
                        if "images" in node_out:
                            img = node_out["images"][0]
                            path = COMFY_OUT / img["filename"]
                            if path.exists():
                                elapsed = round(time.time() - start, 1)
                                print(f"  ✅ SVD done in {elapsed}s")
                                return path
        except:
            pass
    raise TimeoutError("SVD timeout")

print("🎬 SVD XT True Motion Pipeline")
print("=" * 50)
print(f"Animating {len(images)} Juggernaut XL images...")
print("Expected: ~45-60s per image\n")

for i, img in enumerate(images, 1):
    print(f"Scene {i}: {img}")
    
    # Copy to input
    src = COMFY_OUT / img
    dst = COMFY_INPUT / img
    shutil.copy(src, dst)
    
    # Run SVD
    wf = build_svd_workflow(img)
    result = queue_and_wait(wf)
    print(f"  Output: {result.name}\n")
    
    # VRAM settle
    time.sleep(5)

print("✅ All scenes animated with TRUE AI motion!")
print("Files in:", COMFY_OUT)
