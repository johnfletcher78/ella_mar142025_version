#!/usr/bin/env python3
"""
agent_a_sdxl.py — Sub-Agent A: SDXL Image Generation Only
Generates all images, exits, VRAM cleared automatically
"""

import sys
import json
import shutil
from pathlib import Path

# Setup paths
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import urllib.request
import time

COMFY_URL = "http://127.0.0.1:8188"

def main():
    job_dir = Path(sys.argv[1])
    print(f"[Agent A] Starting — SDXL Image Generation")
    print(f"[Agent A] Job directory: {job_dir}")
    
    # Load prompts
    with open(job_dir / "prompts.json") as f:
        prompts = json.load(f)
    
    print(f"[Agent A] Generating {len(prompts)} images with Juggernaut XL v9")
    
    # Enhanced negative prompt from Claude
    NEGATIVE = (
        "deformed, bad anatomy, disfigured, poorly drawn face, "
        "mutation, mutated, extra limbs, extra arms, extra hands, "
        "extra fingers, missing arms, missing hands, missing fingers, "
        "fused fingers, too many fingers, long neck, "
        "malformed limbs, malformed hands, cloned face, "
        "ugly, blurry, watermark, text, signature, "
        "low quality, worst quality, jpeg artifacts, "
        "horizontal composition, landscape orientation, "
        "out of frame, cropped, cut off"
    )
    
    images_dir = job_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    for i, prompt in enumerate(prompts):
        print(f"\n[Agent A] Scene {i+1}/{len(prompts)}: {prompt[:50]}...")
        
        # Build ComfyUI workflow
        seed = int(time.time() * 1000) % 2147483647
        workflow = {
            "1": {"class_type": "CheckpointLoaderSimple", 
                  "inputs": {"ckpt_name": "juggernaut-xl/Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
            "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["1", 1]}},
            "4": {"class_type": "EmptyLatentImage", 
                  "inputs": {"width": 768, "height": 1344, "batch_size": 1}},
            "5": {"class_type": "KSampler", 
                  "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
                            "latent_image": ["4", 0], "seed": seed, "steps": 30, "cfg": 7.5,
                            "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
            "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
            "7": {"class_type": "SaveImage", 
                  "inputs": {"images": ["6", 0], "filename_prefix": f"scene_{i:02d}"}}
        }
        
        # Queue and wait
        import uuid
        payload = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
        req = urllib.request.Request(f"{COMFY_URL}/prompt", data=payload,
                                    headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            prompt_id = json.loads(resp.read())["prompt_id"]
        
        # Wait for completion
        start = time.time()
        timeout = 180
        output_filename = None
        
        while time.time() - start < timeout:
            time.sleep(2)
            try:
                with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}", timeout=5) as resp:
                    history = json.loads(resp.read())
                    if prompt_id in history and "outputs" in history[prompt_id]:
                        for node_out in history[prompt_id]["outputs"].values():
                            if "images" in node_out:
                                img = node_out["images"][0]
                                output_filename = img["filename"]
                                elapsed = round(time.time() - start, 1)
                                print(f"[Agent A] ✅ Done in {elapsed}s: {output_filename}")
                                break
                        if output_filename:
                            break
            except:
                pass
        
        # Copy image from ComfyUI output to job directory
        if output_filename:
            COMFY_OUT = Path.home() / "ComfyUI" / "output"
            src = COMFY_OUT / output_filename
            dst = images_dir / f"scene_{i:02d}.png"
            if src.exists():
                shutil.copy(src, dst)
                print(f"[Agent A] 📁 Copied to: {dst.name}")
            else:
                print(f"[Agent A] ⚠️ Source not found: {src}")
    
    print(f"\n[Agent A] All {len(prompts)} images generated")
    print("[Agent A] Exiting — VRAM will be fully cleared")
    return 0

if __name__ == "__main__":
    sys.exit(main())
