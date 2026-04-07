#!/usr/bin/env python3
"""
Create summer beer video from 3 AI-generated images
- 3 scenes x 5 seconds each = 15 second total
- Add motion to each image (Ken Burns effect)
- Splice together with transitions
"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import numpy as np
import os
from PIL import Image
from moviepy import *
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import AudioClip

# Paths
INPUT_DIR = "/home/bull/ComfyUI/output"
OUTPUT_DIR = "/home/bull/.openclaw/workspace/output"
OUTPUT_PATH = f"{OUTPUT_DIR}/summer_beer_final.mp4"

# Video specs
WIDTH = 1080
HEIGHT = 1920  # 9:16 vertical for Shorts
FPS = 30
SCENE_DURATION = 5  # seconds per scene

def load_and_resize_image(path, target_size=(WIDTH, HEIGHT)):
    """Load image and resize to fit vertical 9:16 format"""
    img = Image.open(path)
    
    # Calculate resize to fill vertical while maintaining aspect ratio
    img_w, img_h = img.size
    target_w, target_h = target_size
    
    # Scale to fill height
    scale = target_h / img_h
    new_w = int(img_w * scale)
    new_h = target_h
    
    # Resize
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
    
    # Crop/pad to exact width
    if new_w > target_w:
        # Crop center
        left = (new_w - target_w) // 2
        img_cropped = img_resized.crop((left, 0, left + target_w, new_h))
    else:
        # Pad with black
        img_cropped = Image.new('RGB', target_size, (0, 0, 0))
        paste_x = (target_w - new_w) // 2
        img_cropped.paste(img_resized, (paste_x, 0))
    
    return np.array(img_cropped)

def create_ken_burns_clip(image_array, duration, zoom_start=1.0, zoom_end=1.1, 
                          pan_x=0, pan_y=0):
    """Create a clip with Ken Burns effect (slow zoom/pan)"""
    from moviepy.video.VideoClip import VideoClip
    
    def make_frame(t):
        progress = t / duration
        zoom = zoom_start + (zoom_end - zoom_start) * progress
        
        # Calculate crop region
        h, w = image_array.shape[:2]
        new_w = int(w / zoom)
        new_h = int(h / zoom)
        
        # Center crop with optional pan
        x1 = (w - new_w) // 2 + int(pan_x * progress)
        y1 = (h - new_h) // 2 + int(pan_y * progress)
        x2 = x1 + new_w
        y2 = y1 + new_h
        
        # Ensure bounds
        x1 = max(0, min(x1, w - new_w))
        y1 = max(0, min(y1, h - new_h))
        x2 = min(w, x1 + new_w)
        y2 = min(h, y1 + new_h)
        
        # Crop and resize
        cropped = image_array[y1:y2, x1:x2]
        
        # Resize to output size
        from PIL import Image
        pil_img = Image.fromarray(cropped)
        pil_resized = pil_img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        
        return np.array(pil_resized)
    
    return VideoClip(make_frame, duration=duration)

# Load the 3 generated images
print("Loading AI-generated images...")
scene1_img = load_and_resize_image(f"{INPUT_DIR}/summer_scene_1_00001_.png")
scene2_img = load_and_resize_image(f"{INPUT_DIR}/summer_scene_2_00001_.png")
scene3_img = load_and_resize_image(f"{INPUT_DIR}/summer_scene_3_00001_.png")

print("Creating clips with Ken Burns effect...")

# Scene 1: Slow zoom out + slight pan
clip1 = create_ken_burns_clip(scene1_img, SCENE_DURATION, 
                               zoom_start=1.15, zoom_end=1.0, 
                               pan_x=50, pan_y=0)

# Scene 2: Slow zoom in
clip2 = create_ken_burns_clip(scene2_img, SCENE_DURATION,
                               zoom_start=1.0, zoom_end=1.12,
                               pan_x=0, pan_y=0)

# Scene 3: Gentle zoom out
clip3 = create_ken_burns_clip(scene3_img, SCENE_DURATION,
                               zoom_start=1.1, zoom_end=1.0,
                               pan_x=-30, pan_y=20)

# Concatenate the clips
from moviepy import concatenate_videoclips
print("Splicing clips together...")
final_video = concatenate_videoclips([clip1, clip2, clip3])

# Add upbeat summer audio
def make_summer_beat(t):
    """Generate a simple upbeat summer beat"""
    # A major chord progression with rhythm
    beat = np.sin(2 * np.pi * 440 * t) * 0.25  # A4
    beat += np.sin(2 * np.pi * 554 * t) * 0.20  # C#5
    beat += np.sin(2 * np.pi * 659 * t) * 0.20  # E5
    
    # Add some rhythm variation
    beat *= (0.6 + 0.4 * np.sin(2 * np.pi * 2.5 * t) ** 2)
    
    return np.clip(beat, -1, 1)

audio = AudioClip(make_summer_beat, duration=SCENE_DURATION * 3).with_fps(44100)
final_video = final_video.with_audio(audio)

# Export
print(f"Exporting final video to {OUTPUT_PATH}...")
final_video.write_videofile(
    OUTPUT_PATH,
    fps=FPS,
    codec='libx264',
    audio_codec='aac',
    threads=4,
    preset='medium'
)

print(f"\n✅ Summer beer video complete!")
print(f"Duration: {SCENE_DURATION * 3}s | Resolution: {WIDTH}x{HEIGHT}")
print(f"Scenes: Beach sunset → Poolside → Campfire")
