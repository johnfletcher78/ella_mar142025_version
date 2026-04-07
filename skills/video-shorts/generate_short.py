#!/usr/bin/env python3
"""generate_short.py — Simplified pipeline for Ella"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import os
import json
import time
import subprocess
import urllib.request
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Config
COMFY_URL = "http://127.0.0.1:8188"
OLLAMA_URL = "http://localhost:11434"
OUTPUT_DIR = Path.home() / "videos" / "shorts"
COMFY_OUT = Path.home() / "ComfyUI" / "output"
VIDEO_W, VIDEO_H = 1080, 1920
CLIP_DUR = 5

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
        print("[vram] ABORT: Need 2GB+ free")
        return False
    return True

def comfy_interrupt():
    try:
        req = urllib.request.Request(f"{COMFY_URL}/interrupt", data=b"{}", method="POST")
        urllib.request.urlopen(req, timeout=5)
        time.sleep(5)
        print("[vram] Interrupt sent")
    except Exception as e:
        print(f"[vram] Interrupt failed: {e}")

def generate_script(topic):
    """Ask Kimi for 3 scenes"""
    system = ("You are a YouTube Shorts scriptwriter. Write a 3-scene script. "
              "Return ONLY JSON: [{\"scene\":1,\"image_prompt\":\"...\","
              "\"narration_text\":\"...\",\"caption_text\":\"...\"},...]")
    payload = json.dumps({"model": "kimi-k2.5:cloud", "system": system, 
                         "prompt": f"Topic: {topic}", "stream": False}).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=payload,
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read())["response"].strip()
            if "```" in raw: raw = raw.split("```")[1]
            start, end = raw.find("["), raw.rfind("]") + 1
            return json.loads(raw[start:end])
    except Exception as e:
        print(f"[script] Error: {e}")
        return []

def build_sdxl_workflow(prompt, seed=-1):
    if seed == -1: seed = int(time.time() * 1000) % 2147483647
    return {
        "1": {"class_type": "CheckpointLoaderSimple", 
              "inputs": {"ckpt_name": "sd_xl_base.safetensors"}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": f"{prompt}, vertical 9:16, cinematic", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": "ugly, blurry, horizontal, low quality", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": VIDEO_W, "height": VIDEO_H, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
                        "latent_image": ["4", 0], "seed": seed, "steps": 30, "cfg": 7.5,
                        "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "short_scene"}}
    }

def queue_workflow(wf, timeout=120):
    payload = json.dumps({"prompt": wf, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=payload,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        pid = json.loads(resp.read())["prompt_id"]
    
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(2)
        try:
            with urllib.request.urlopen(f"{COMFY_URL}/history/{pid}", timeout=5) as resp:
                hist = json.loads(resp.read())
                if pid in hist and "outputs" in hist[pid]:
                    for node in hist[pid]["outputs"].values():
                        if "images" in node:
                            img = node["images"][0]
                            path = COMFY_OUT / img["filename"]
                            if path.exists():
                                return path
        except:
            pass
    raise TimeoutError("ComfyUI timeout")

def create_short(topic):
    print(f"\n🎬 Creating Short: {topic}")
    
    if not check_vram():
        return {"success": False, "error": "Low VRAM"}
    
    job_id = f"short_{int(time.time())}"
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Script
    print("\n📝 Generating script...")
    scenes = generate_script(topic)
    print(f"  {len(scenes)} scenes")
    
    # Step 2: Images
    print("\n🎨 Generating images...")
    imgs = []
    for s in scenes:
        print(f"  Scene {s['scene']}: {s['caption_text']}")
        wf = build_sdxl_workflow(s["image_prompt"])
        src = queue_workflow(wf)
        dest = job_dir / f"scene_{s['scene']:02d}.png"
        shutil.copy(src, dest)
        imgs.append(dest)
    comfy_interrupt()
    
    # Step 3: SVD animation (simplified - needs SVD model installed)
    print("\n🎥 [SVD would run here - model downloading...]")
    
    return {"success": True, "job_id": job_id, "scenes": len(scenes), "images": [str(i) for i in imgs]}

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "summer and beer"
    result = create_short(topic)
    print(json.dumps(result))
