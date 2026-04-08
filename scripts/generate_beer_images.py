#!/usr/bin/env python3
"""Generate 3 beer commercial images with detailed prompts"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import json
import urllib.request
import time

COMFY_URL = "http://127.0.0.1:8188"

# Claude's detailed prompts
prompts = [
    {
        "name": "scene_01_friends_patio",
        "prompt": "two friends laughing together on a sunny outdoor patio, holding cold beer bottles with condensation, casual summer clothing, warm golden afternoon sunlight, shallow depth of field, medium shot, photorealistic, Nikon D850 style photography, bokeh background of green trees and patio furniture, warm amber tones, joyful candid moment, ultra detailed, sharp focus, 8K quality, vertical portrait composition, 9:16 aspect ratio"
    },
    {
        "name": "scene_02_money_shot", 
        "prompt": "close up of hand holding ice cold craft beer bottle with water droplets and condensation, golden sunset background, warm orange and amber lighting, beer label catching sunlight, bokeh background, photorealistic, product photography style, shallow depth of field, vertical composition, cinematic color grading, ultra detailed, 9:16 aspect ratio"
    },
    {
        "name": "scene_03_group_toast",
        "prompt": "small group of three friends toasting beer bottles at an outdoor rooftop bar at sunset, smiling faces, casual summer outfits, warm golden hour lighting from behind, cinematic wide shot, shallow depth of field, blurred city skyline in background, photorealistic, vibrant summer colors, vertical portrait composition, 9:16 aspect ratio"
    }
]

def build_workflow(prompt, filename):
    seed = int(time.time() * 1000) % 2147483647
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "ugly, blurry, horizontal, low quality, worst quality, jpeg artifacts, deformed, extra limbs", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1080, "height": 1920, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0], "seed": seed, "steps": 30, "cfg": 7.5, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": filename}}
    }

def queue_and_wait(workflow, timeout=180):
    import uuid
    payload = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=payload, headers={"Content-Type": "application/json"})
    
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
    raise TimeoutError("Timeout waiting for image")

print("🎨 Generating 3 beer commercial images with detailed prompts...\n")

generated = []
for i, p in enumerate(prompts, 1):
    print(f"Scene {i}: {p['name']}")
    wf = build_workflow(p["prompt"], p["name"])
    filename = queue_and_wait(wf)
    generated.append({"scene": i, "name": p["name"], "file": filename})
    time.sleep(1)  # brief pause between generations

print(f"\n✅ All {len(generated)} images generated!")
print("Files saved to: ~/ComfyUI/output/")
for g in generated:
    print(f"  Scene {g['scene']}: {g['file']}")
