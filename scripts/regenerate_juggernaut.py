#!/usr/bin/env python3
"""Regenerate beer images with Juggernaut XL v9 (better anatomy)"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import json
import urllib.request
import time

COMFY_URL = "http://127.0.0.1:8188"

# Product-focused prompts (no people)
prompts = [
    {
        "name": "jug_scene_01_hero",
        "prompt": "ice cold craft beer bottle standing upright on a wooden bar top outdoors, water droplets and condensation dripping down the bottle, warm golden sunset bokeh background, dramatic product photography, ray of sunlight hitting the bottle, amber and gold color palette, shallow depth of field, ultra detailed, sharp focus, vertical portrait composition, 9:16 aspect ratio"
    },
    {
        "name": "jug_scene_02_atmosphere", 
        "prompt": "outdoor summer patio bar scene at golden hour, string lights overhead, wooden tables with beer glasses, nobody in frame, warm amber sunlight streaming through trees, shallow depth of field, cinematic color grading, peaceful summer evening atmosphere, vertical portrait composition, 9:16, ultra detailed"
    },
    {
        "name": "jug_scene_03_hands",
        "prompt": "close up of three hands holding beer bottles clinking together in a toast, outdoor summer setting, golden hour sunlight, condensation on bottles, photorealistic, product photography style, warm tones, ultra detailed, vertical portrait composition, 9:16 aspect ratio"
    }
]

# Enhanced negative prompt from Claude
NEGATIVE = (
    "deformed, bad anatomy, disfigured, poorly drawn face, "
    "mutation, mutated, extra limbs, extra arms, extra hands, "
    "extra fingers, missing arms, missing hands, missing fingers, "
    "fused fingers, too many fingers, long neck, "
    "malformed limbs, malformed hands, cloned face, "
    "four arms, three arms, six fingers, four hands, "
    "poorly drawn hands, bad hands, wrong hands, "
    "mutant hands, mutilated hands, deformed hands, "
    "ugly, blurry, watermark, text, signature, "
    "low quality, worst quality, jpeg artifacts, "
    "grainy, overexposed, underexposed, duplicate, "
    "horizontal composition, landscape orientation, "
    "out of frame, cropped, cut off"
)

def build_workflow(prompt, filename):
    """Use Juggernaut XL v9"""
    seed = int(time.time() * 1000) % 2147483647
    return {
        "1": {"class_type": "CheckpointLoaderSimple", 
              "inputs": {"ckpt_name": "juggernaut-xl/Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1080, "height": 1920, "batch_size": 1}},
        "5": {"class_type": "KSampler", 
              "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], 
                        "latent_image": ["4", 0], "seed": seed, "steps": 30, "cfg": 7.5, 
                        "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": filename}}
    }

def queue_and_wait(workflow, timeout=180):
    import uuid
    payload = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=payload,
                                headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        prompt_id = json.loads(resp.read())["prompt_id"]
    
    print(f"  Queued: {prompt_id}")
    start = time.time()
    
    while time.time() - start < timeout:
        time.sleep(2)
        try:
            with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}", timeout=5) as resp:
                history = json.loads(resp.read())
                if prompt_id in history and "outputs" in history[prompt_id]:
                    for node_out in history[prompt_id]["outputs"].values():
                        if "images" in node_out:
                            img = node_out["images"][0]
                            print(f"  ✅ Done in {round(time.time()-start,1)}s: {img['filename']}")
                            return img["filename"]
        except:
            pass
    raise TimeoutError("Timeout")

print("🎨 Regenerating with JUGGERNAUT XL v9 (better anatomy)...\n")

for i, p in enumerate(prompts, 1):
    print(f"Scene {i}: {p['name']}")
    wf = build_workflow(p["prompt"], p["name"])
    filename = queue_and_wait(wf)
    print(f"  File: {filename}\n")
    time.sleep(1)

print("✅ All 3 images regenerated with Juggernaut XL!")
print("Better anatomy, fewer hand/finger issues.")
