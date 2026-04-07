#!/usr/bin/env python3
"""
Create 15-second beer short NOW using available tools.
Uses Ken Burns effect while SVD XT downloads.
"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import *
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import AudioClip

INPUT_DIR = "/home/bull/ComfyUI/output"
OUTPUT_PATH = "/home/bull/.openclaw/workspace/output/beer_short_ready_now.mp4"

WIDTH, HEIGHT = 1080, 1920
DURATION = 15

def create_text_img(text, size, font_size=90, color=(255,255,255), stroke=(0,0,0)):
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x, y = (size[0]-tw)//2, (size[1]-th)//2
    for dx in range(-4,5):
        for dy in range(-4,5):
            if dx*dx+dy*dy <= 16:
                draw.text((x+dx,y+dy), text, font=font, fill=stroke)
    draw.text((x,y), text, font=font, fill=color)
    return np.array(img)

def ken_burns(img_arr, dur, z1=1.0, z2=1.15, pan=(0,0)):
    from moviepy.video.VideoClip import VideoClip
    def frame(t):
        p = t/dur
        ease = p*p*(3-2*p)
        z = z1 + (z2-z1)*ease
        h,w = img_arr.shape[:2]
        nw, nh = int(w/z), int(h/z)
        x = int((w-nw)*0.5 + pan[0]*ease)
        y = int((h-nh)*0.5 + pan[1]*ease)
        x,y = max(0,min(x,w-nw)), max(0,min(y,h-nh))
        cropped = img_arr[y:y+nh, x:x+nw]
        return np.array(Image.fromarray(cropped).resize((WIDTH,HEIGHT), Image.LANCZOS))
    return VideoClip(frame, duration=dur)

# Load existing beer images
print("Loading beer images...")
scene1 = np.array(Image.open(f"{INPUT_DIR}/summer_scene_1_00001_.png").resize((WIDTH,HEIGHT)))
scene2 = np.array(Image.open(f"{INPUT_DIR}/summer_scene_2_00001_.png").resize((WIDTH,HEIGHT)))
scene3 = np.array(Image.open(f"{INPUT_DIR}/summer_scene_3_00001_.png").resize((WIDTH,HEIGHT)))

# Create text overlays
t1 = create_text_img("ICE COLD", (WIDTH,200), 100, (255,255,255), (255,140,0))
t2 = create_text_img("SUMMER VIBES", (WIDTH,200), 100, (255,220,100), (0,0,0))
t3 = create_text_img("PERFECT COMBO", (WIDTH,200), 100, (255,255,255), (50,150,255))

from moviepy.video.VideoClip import ImageClip

# Scene 1: Beach sunset - zoom out + pan left
bg1 = ken_burns(scene1, 5, 1.2, 1.0, (-100,0))
txt1 = ImageClip(t1).with_duration(5).with_position(('center',800))
clip1 = CompositeVideoClip([bg1, txt1])

# Scene 2: Poolside - zoom in
txt2 = ImageClip(t2).with_duration(5).with_position(('center',900))
bg2 = ken_burns(scene2, 5, 1.0, 1.15, (0,50))
clip2 = CompositeVideoClip([bg2, txt2])

# Scene 3: Campfire - gentle zoom out + rotation hint
txt3 = ImageClip(t3).with_duration(5).with_position(('center',700))
bg3 = ken_burns(scene3, 5, 1.1, 1.0, (50,-30))
clip3 = CompositeVideoClip([bg3, txt3])

# Concatenate
from moviepy import concatenate_videoclips
final = concatenate_videoclips([clip1, clip2, clip3])

# Summer beat audio
def beat(t):
    if hasattr(t, '__len__'): t = t[0] if len(t) > 0 else 0
    scene = int(t/5)
    b = np.sin(2*np.pi*440*t)*0.25 + np.sin(2*np.pi*554*t)*0.2 + np.sin(2*np.pi*659*t)*0.2
    vol = [0.5, 0.7, 0.5][min(scene,2)]
    return np.clip(b*vol, -1, 1)

final = final.with_audio(AudioClip(beat, duration=15).with_fps(44100))

print("Exporting...")
final.write_videofile(OUTPUT_PATH, fps=30, codec='libx264', audio_codec='aac', threads=4)
print(f"✅ Ready: {OUTPUT_PATH}")
