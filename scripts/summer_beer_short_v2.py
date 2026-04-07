#!/usr/bin/env python3
"""
Create a 15-second YouTube Short about summertime and cold beer.
Version 2: Using PIL/Pillow for text rendering (more reliable than TextClip)
"""

import sys
sys.path.insert(0, '/home/bull/.local/lib/python3.13/site-packages')

import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import *
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import AudioClip

# Output path
output_path = "/home/bull/.openclaw/workspace/output/summer_beer_short_v2.mp4"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# YouTube Shorts specs: 9:16 aspect ratio, 1080x1920
WIDTH = 1080
HEIGHT = 1920
DURATION = 15  # seconds
FPS = 30

def create_text_image(text, size, font_size=80, text_color=(255, 255, 255), 
                      stroke_color=(0, 0, 0), stroke_width=4, bg_color=None):
    """Create an image with text using PIL."""
    img = Image.new('RGBA', size, bg_color if bg_color else (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw stroke (outline)
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx*dx + dy*dy <= stroke_width*stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=text_color)
    
    return np.array(img)

# Create gradient background
def make_frame(t):
    """Create summer sunset gradient background."""
    y = np.linspace(0, 1, HEIGHT)
    x = np.linspace(0, 1, WIDTH)
    X, Y = np.meshgrid(x, y)
    
    # Summer sunset: warm orange/yellow at top, cool blue at bottom
    r = np.clip(1.0 - Y * 0.4 + 0.2, 0, 1)
    g = np.clip(0.5 - Y * 0.2 + 0.3, 0, 1)
    b = np.clip(0.1 + Y * 0.7, 0, 1)
    
    frame = np.stack([r, g, b], axis=2) * 255
    return frame.astype(np.uint8)

# Main background
from moviepy.video.VideoClip import VideoClip
background = VideoClip(make_frame, duration=DURATION)

# Create text images using PIL
text1_img = create_text_image("☀️ SUMMER VIBES ☀️", (WIDTH, 200), font_size=90,
                               text_color=(255, 255, 255), stroke_color=(255, 140, 0), stroke_width=5)
text2_img = create_text_image("ICE COLD BEER", (WIDTH, 200), font_size=110,
                               text_color=(255, 220, 100), stroke_color=(0, 0, 0), stroke_width=6)
text3_img = create_text_image("PERFECT COMBO!", (WIDTH, 200), font_size=100,
                               text_color=(255, 255, 255), stroke_color=(50, 150, 255), stroke_width=5)

# Create ImageClips from the PIL images
from moviepy.video.VideoClip import ImageClip

# Text clips with crossfade using masks
text1_raw = ImageClip(text1_img).with_duration(5).with_start(0).with_position(('center', 500))
text2_raw = ImageClip(text2_img).with_duration(6).with_start(4).with_position(('center', 700))
text3_raw = ImageClip(text3_img).with_duration(6).with_start(9).with_position(('center', 600))

# Beer emoji
beer_img = create_text_image("🍺", (200, 200), font_size=180, 
                              text_color=(255, 200, 100), stroke_color=(139, 69, 19), stroke_width=3)
beer = ImageClip(beer_img).with_duration(DURATION).with_position(('center', 1000))

# Combine all elements
video = CompositeVideoClip([
    background,
    beer,
    text1_raw,
    text2_raw,
    text3_raw
], size=(WIDTH, HEIGHT))

# Add upbeat summer audio
def make_summer_beat(t):
    """Generate a simple upbeat summer beat."""
    beat = np.sin(2 * np.pi * 440 * t) * 0.25
    beat += np.sin(2 * np.pi * 554 * t) * 0.2
    beat += np.sin(2 * np.pi * 659 * t) * 0.2
    beat *= (0.5 + 0.5 * np.sin(2 * np.pi * 2 * t) ** 2)
    return np.clip(beat, -1, 1)

audio = AudioClip(make_summer_beat, duration=DURATION).with_fps(44100)
video = video.with_audio(audio)

# Export as YouTube Short
print("Rendering improved 15-second YouTube Short...")
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
