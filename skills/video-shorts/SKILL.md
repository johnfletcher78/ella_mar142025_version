# YouTube Shorts & Reels Production Skill
**For: OpenClaw Bot (Ella) | Linux | RTX 4080 16GB VRAM**
**Models: DreamShaper XL + Stable Video Diffusion XT**

## Overview
Produces complete YouTube Shorts from text prompts using SVD XT for real motion.

## Performance
- Image generation: ~8-10s per image
- SVD animation: ~45-60s per clip
- Total: 3.5-4.5 minutes for 15s video
- Peak VRAM: ~14GB

## Trigger
- "make a YouTube Short about..."
- "create a Reel for..."

## Setup Required
1. Download SVD XT model (~10GB)
2. Install edge-tts, Pillow
3. Verify ComfyUI running

## Files
- generate_short.py — pipeline
- run.mjs — OpenClaw entry
- cleanup.py — purge tool

See full SKILL.md for complete documentation.
