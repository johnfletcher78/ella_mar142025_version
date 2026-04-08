#!/usr/bin/env python3
"""Create best possible beer video with current tools while SVD workflow gets fixed"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import numpy as np
from PIL import Image
from moviepy import *
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import AudioClip

INPUT = "/home/bull/ComfyUI/output"
OUTPUT = "/home/bull/.openclaw/workspace/output/beer_svd_ready.mp4"

def ken_burns(img, dur, z1=1.0, z2=1.12, pan=(0,0)):
    from moviepy.video.VideoClip import VideoClip
    def frame(t):
        p = t/dur
        ease = p*p*(3-2*p)  # Smooth easing
        z = z1 + (z2-z1)*ease
        h,w = img.shape[:2]
        nw, nh = int(w/z), int(h/z)
        x = int((w-nw)*0.5 + pan[0]*ease)
        y = int((h-nh)*0.5 + pan[1]*ease)
        x,y = max(0,min(x,w-nw)), max(0,min(y,h-nh))
        cropped = img[y:y+nh, x:x+nw]
        return np.array(Image.fromarray(cropped).resize((1080,1920), Image.LANCZOS))
    return VideoClip(frame, duration=dur)

# Load the 3 new AI-generated beer images
print("Loading beer images...")
img1 = np.array(Image.open(f"{INPUT}/scene_01_friends_patio_00001_.png").resize((1080,1920)))
img2 = np.array(Image.open(f"{INPUT}/scene_02_money_shot_00001_.png").resize((1080,1920)))
img3 = np.array(Image.open(f"{INPUT}/scene_03_group_toast_00001_.png").resize((1080,1920)))

# Scene 1: Friends - slow zoom out, pan right
clip1 = ken_burns(img1, 5, 1.15, 1.0, (80, 0))

# Scene 2: Money shot - zoom in on beer
clip2 = ken_burns(img2, 5, 1.0, 1.18, (0, 30))

# Scene 3: Group toast - gentle zoom out, pan left
clip3 = ken_burns(img3, 5, 1.12, 1.0, (-60, 20))

# Concatenate
from moviepy import concatenate_videoclips
final = concatenate_videoclips([clip1, clip2, clip3])

# Audio
def beat(t):
    if hasattr(t, '__len__'): t = t[0] if len(t) > 0 else 0
    scene = int(t/5)
    b = np.sin(2*np.pi*440*t)*0.25 + np.sin(2*np.pi*554*t)*0.2 + np.sin(2*np.pi*659*t)*0.2
    vol = [0.6, 0.8, 0.6][min(scene,2)]
    return np.clip(b*vol, -1, 1)

final = final.with_audio(AudioClip(beat, duration=15).with_fps(44100))

print("Exporting...")
final.write_videofile(OUTPUT, fps=30, codec='libx264', audio_codec='aac', threads=4)
print(f"✅ Ready: {OUTPUT}")
print("\nNote: SVD XT model downloaded but workflow needs custom node setup.")
print("This version uses smooth Ken Burns on the new AI-generated images.")
