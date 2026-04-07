#!/usr/bin/env python3
"""
Create a 15-second YouTube Short about summertime and cold beer.
Uses MoviePy for video assembly with text overlays.
"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import numpy as np
import os

# Import moviepy components
from moviepy.video.VideoClip import VideoClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.FadeIn import FadeIn
from moviepy.video.fx.FadeOut import FadeOut
from moviepy.audio.AudioClip import AudioClip

# Output path
output_path = "/home/bull/.openclaw/workspace/output/summer_beer_short.mp4"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# YouTube Shorts specs: 9:16 aspect ratio, 1080x1920
WIDTH = 1080
HEIGHT = 1920
DURATION = 15  # seconds
FPS = 30

# Create a gradient background (summer vibes - warm orange to cool blue)
def make_frame(t):
    # Orange/yellow to blue gradient (sunset vibes)
    y = np.linspace(0, 1, HEIGHT)
    x = np.linspace(0, 1, WIDTH)
    X, Y = np.meshgrid(x, y)
    
    # Summer sunset gradient
    r = np.clip(1.0 - Y * 0.5 + 0.3, 0, 1)
    g = np.clip(0.6 - Y * 0.3 + 0.2, 0, 1)
    b = np.clip(0.2 + Y * 0.6, 0, 1)
    
    frame = np.stack([r, g, b], axis=2) * 255
    return frame.astype(np.uint8)

# Main background
background = VideoClip(make_frame, duration=DURATION)

# Create text using ImageClip since TextClip needs ImageMagick
try:
    from moviepy.video.VideoClip import TextClip
    
    # Text clip 1
    text1 = TextClip(
        text="☀️ SUMMER VIBES ☀️",
        font_size=80,
        color='white',
        font='DejaVu-Sans-Bold',
        stroke_color='orange',
        stroke_width=3
    ).with_duration(5).with_position(('center', 600))
    text1 = FadeIn(text1, duration=0.5)
    text1 = FadeOut(text1, duration=0.5)
    
    # Text clip 2
    text2 = TextClip(
        text="ICE COLD BEER 🍺",
        font_size=90,
        color='yellow',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=4
    ).with_start(4).with_duration(6).with_position(('center', 700))
    text2 = FadeIn(text2, duration=0.5)
    text2 = FadeOut(text2, duration=0.5)
    
    # Text clip 3
    text3 = TextClip(
        text="PERFECT COMBO! 🌴",
        font_size=80,
        color='white',
        font='DejaVu-Sans-Bold',
        stroke_color='blue',
        stroke_width=3
    ).with_start(9).with_duration(6).with_position(('center', 600))
    text3 = FadeIn(text3, duration=0.5)
    text3 = FadeOut(text3, duration=1)
    
    # Beer emoji
    beer = TextClip(
        text="🍺",
        font_size=200,
        color='white'
    ).with_duration(DURATION).with_position(('center', 1000))
    
except Exception as e:
    print(f"TextClip error: {e}")
    print("Using ColorClip fallback for text...")
    text1 = ColorClip(size=(800, 100), color=(255, 165, 0)).with_duration(5).with_position(('center', 600))
    text2 = ColorClip(size=(800, 100), color=(255, 255, 0)).with_start(4).with_duration(6).with_position(('center', 700))
    text3 = ColorClip(size=(800, 100), color=(100, 200, 255)).with_start(9).with_duration(6).with_position(('center', 600))
    beer = ColorClip(size=(200, 200), color=(255, 200, 100)).with_duration(DURATION).with_position(('center', 1000))

# Combine all elements
video = CompositeVideoClip([
    background,
    beer,
    text1,
    text2,
    text3
], size=(WIDTH, HEIGHT))

# Add upbeat summer audio
def make_summer_beat(t):
    beat = np.sin(2 * np.pi * 440 * t) * 0.3
    beat += np.sin(2 * np.pi * 554 * t) * 0.2
    beat += np.sin(2 * np.pi * 659 * t) * 0.2
    beat *= (0.5 + 0.5 * np.sin(2 * np.pi * 2 * t) ** 2)
    return np.clip(beat, -1, 1)

audio = AudioClip(make_summer_beat, duration=DURATION).with_fps(44100)
video = video.with_audio(audio)

# Export as YouTube Short
print("Rendering 15-second YouTube Short...")
video.write_videofile(
    output_path,
    fps=FPS,
    codec='libx264',
    audio_codec='aac',
    threads=4,
    preset='medium'
)

print(f"\n✅ YouTube Short created: {output_path}")
print(f"Duration: {DURATION}s | Resolution: {WIDTH}x{HEIGHT} (9:16)")
