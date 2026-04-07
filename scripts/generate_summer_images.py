#!/usr/bin/env python3
"""
Generate summer beer images using ComfyUI API
"""

import requests
import json
import time
import os

COMFY_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = "/home/bull/.openclaw/workspace/output"

# Three scenes for the video
scenes = [
    "friends toasting with beer glasses at beach sunset, summer vibes, warm golden hour lighting, photorealistic, 4k, candid moment",
    "close up of cold beer bottle with condensation drops, poolside summer party, people laughing in background blur, tropical setting",
    "group of friends enjoying beers around campfire at night, summer camping, warm fire glow, stars visible, relaxed atmosphere"
]

def generate_image(prompt, filename):
    """Generate image using ComfyUI API"""
    
    # Simple workflow for SDXL
    workflow = {
        "1": {
            "inputs": {
                "text": prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "2": {
            "inputs": {
                "text": "blurry, low quality, distorted, ugly",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "3": {
            "inputs": {
                "seed": 42,
                "steps": 30,
                "cfg": 7.0,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["1", 0],
                "negative": ["2", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "sd_xl_base.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "7": {
            "inputs": {
                "filename_prefix": filename,
                "images": ["6", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    # Queue the prompt
    response = requests.post(f"{COMFY_URL}/prompt", json={"prompt": workflow})
    if response.status_code == 200:
        prompt_id = response.json()["prompt_id"]
        print(f"Queued {filename}, prompt ID: {prompt_id}")
        return prompt_id
    else:
        print(f"Failed to queue: {response.text}")
        return None

# Check if ComfyUI is running
try:
    response = requests.get(f"{COMFY_URL}/system_stats", timeout=5)
    print(f"ComfyUI status: {response.status_code}")
    
    # Generate the three images
    for i, scene in enumerate(scenes):
        filename = f"summer_scene_{i+1}"
        print(f"\nGenerating scene {i+1}: {scene[:50]}...")
        prompt_id = generate_image(scene, filename)
        if prompt_id:
            print(f"  Prompt ID: {prompt_id}")
        time.sleep(2)  # Brief delay between requests
    
    print("\n✅ All three scenes queued!")
    print("Check ComfyUI for output files.")
    
except requests.exceptions.ConnectionError:
    print("❌ ComfyUI not running!")
    print("Start it with: cd /home/bull/ComfyUI && python main.py")
    exit(1)
