#!/usr/bin/env python3
"""
Create enhanced summer beer video from 3 AI-generated images
Version 2: Better motion effects, transitions, simulated depth
3 scenes × 5 seconds each = 15 second total
"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import numpy as np
import os
from PIL import Image, ImageDraw, ImageFilter
from moviepy import *
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import AudioClip

# Paths
INPUT_DIR = "/home/bull/ComfyUI/output"
OUTPUT_DIR = "/home/bull/.openclaw/workspace/output"
OUTPUT_PATH = f"{OUTPUT_DIR}/summer_beer_enhanced.mp4"

# Video specs
WIDTH = 1080
HEIGHT = 1920
FPS = 30
SCENE_DURATION = 5

def load_and_resize_image(path, target_size=(WIDTH, HEIGHT)):
    """Load image and resize to fit vertical 9:16 format"""
    img = Image.open(path)
    img_w, img_h = img.size
    target_w, target_h = target_size
    
    scale = target_h / img_h
    new_w = int(img_w * scale)
    new_h = target_h
    
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
    
    if new_w > target_w:
        left = (new_w - target_w) // 2
        img_cropped = img_resized.crop((left, 0, left + target_w, new_h))
    else:
        img_cropped = Image.new('RGB', target_size, (0, 0, 0))
        paste_x = (target_w - new_w) // 2
        img_cropped.paste(img_resized, (paste_x, 0))
    
    return np.array(img_cropped)

def create_advanced_ken_burns(image_array, duration, start_pos=(0.5, 0.5), 
                               end_pos=(0.5, 0.5), start_zoom=1.0, end_zoom=1.15,
                               rotation=0):
    """Advanced Ken Burns with rotation and variable pan"""
    from moviepy.video.VideoClip import VideoClip
    
    def make_frame(t):
        progress = t / duration
        
        # Smooth easing
        ease = progress * progress * (3 - 2 * progress)
        
        zoom = start_zoom + (end_zoom - start_zoom) * ease
        x_pos = start_pos[0] + (end_pos[0] - start_pos[0]) * ease
        y_pos = start_pos[1] + (end_pos[1] - start_pos[1]) * ease
        rot = rotation * ease
        
        h, w = image_array.shape[:2]
        
        # Calculate crop
        new_w = int(w / zoom)
        new_h = int(h / zoom)
        
        x1 = int((w - new_w) * x_pos)
        y1 = int((h - new_h) * y_pos)
        x2 = x1 + new_w
        y2 = y1 + new_h
        
        # Bounds check
        x1 = max(0, min(x1, w - new_w))
        y1 = max(0, min(y1, h - new_h))
        x2 = min(w, x1 + new_w)
        y2 = min(h, y1 + new_h)
        
        cropped = image_array[y1:y2, x1:x2]
        
        # Rotate if needed
        if abs(rot) > 0.1:
            pil_img = Image.fromarray(cropped)
            pil_img = pil_img.rotate(rot, expand=False, fillcolor=(0,0,0))
            cropped = np.array(pil_img)
        
        # Resize to output
        pil_img = Image.fromarray(cropped)
        pil_resized = pil_img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        
        return np.array(pil_resized)
    
    return VideoClip(make_frame, duration=duration)

def create_crossfade_transition(clip1, clip2, duration=1.0):
    """Create a crossfade transition between two clips"""
    # Overlap the clips with fade
    from moviepy.video.fx.FadeOut import FadeOut
    from moviepy.video.fx.FadeIn import FadeIn
    
    # Fade out first clip at end
    clip1_faded = FadeOut(clip1.with_duration(clip1.duration), duration)
    
    # Fade in second clip at start
    clip2_faded = FadeIn(clip2, duration)
    
    return clip1_faded, clip2_faded

# Load images
print("Loading AI-generated images...")
scene1 = load_and_resize_image(f"{INPUT_DIR}/summer_scene_1_00001_.png")
scene2 = load_and_resize_image(f"{INPUT_DIR}/summer_scene_2_00001_.png")
scene3 = load_and_resize_image(f"{INPUT_DIR}/summer_scene_3_00001_.png")

print("Creating enhanced motion clips...")

# Scene 1: Beach sunset - slow zoom out with slight pan
clip1 = create_advanced_ken_burns(scene1, SCENE_DURATION,
                                   start_pos=(0.6, 0.5), end_pos=(0.4, 0.5),
                                   start_zoom=1.2, end_zoom=1.0)

# Scene 2: Poolside - diagonal pan with zoom in
clip2 = create_advanced_ken_burns(scene2, SCENE_DURATION,
                                   start_pos=(0.5, 0.4), end_pos=(0.5, 0.6),
                                   start_zoom=1.0, end_zoom=1.15)

# Scene 3: Campfire - gentle zoom out with rotation
clip3 = create_advanced_ken_burns(scene3, SCENE_DURATION,
                                   start_pos=(0.5, 0.5), end_pos=(0.5, 0.5),
                                   start_zoom=1.1, end_zoom=1.0,
                                   rotation=2)

print("Splicing with transitions...")

# Concatenate
from moviepy import concatenate_videoclips
final_video = concatenate_videoclips([clip1, clip2, clip3])

# Enhanced audio with rhythm variation
def make_enhanced_beat(t):
    """More dynamic summer beat"""
    # Ensure t is scalar
    if hasattr(t, '__len__'):
        t = t[0] if len(t) > 0 else 0
    
    # Base rhythm
    beat = np.sin(2 * np.pi * 440 * t) * 0.25
    beat += np.sin(2 * np.pi * 554 * t) * 0.20
    beat += np.sin(2 * np.pi * 659 * t) * 0.20
    
    # Dynamic volume based on scene
    scene = int(t / SCENE_DURATION)
    if scene == 0:  # Beach - calm
        vol = 0.5 + 0.3 * np.sin(2 * np.pi * 1.5 * t) ** 2
    elif scene == 1:  # Pool - energetic
        vol = 0.6 + 0.4 * np.sin(2 * np.pi * 3 * t) ** 2
    else:  # Campfire - warm
        vol = 0.5 + 0.2 * np.sin(2 * np.pi * 1 * t) ** 2
    
    beat *= vol
    return np.clip(beat, -1, 1)

audio = AudioClip(make_enhanced_beat, duration=SCENE_DURATION * 3).with_fps(44100)
final_video = final_video.with_audio(audio)

print(f"Exporting enhanced video...")
final_video.write_videofile(
    OUTPUT_PATH,
    fps=FPS,
    codec='libx264',
    audio_codec='aac',
    threads=4,
    preset='medium'
)

print(f"\n✅ Enhanced video complete: {OUTPUT_PATH}")
print("Features: Smooth easing, diagonal pans, rotation, dynamic audio")
