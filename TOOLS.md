# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Video & AI Tools (Local)

### ComfyUI — AI Image/Video Generation
- **Location:** `/home/bull/ComfyUI`
- **Models:** SDXL Base (6.5GB), Dreamshaper XL
- **Can do:** Text-to-image, image-to-image, video generation (needs SVD models)
- **Start:** `cd /home/bull/ComfyUI && python main.py`
- **Custom nodes:** Mostly empty, can add AnimateDiff/SVD nodes

### FFmpeg — Video Processing
- **Path:** `/home/bull/.local/bin/ffmpeg`
- **ffprobe:** Available (for metadata inspection)
- **Use for:** Format conversion, clipping, merging, filters

### MoviePy — Python Video Editing
- **Version:** 2.2.1 (installed April 2025)
- **Use for:** Programmatic video assembly, text overlays, transitions
- **Example:** `/home/bull/.openclaw/workspace/scripts/summer_beer_short.py`
- **Output:** 1080x1920 (9:16) vertical videos for YouTube Shorts

### Python ML Stack
- **torch:** 2.10.0 (with CUDA support)
- **diffusers:** 0.37.0 — HuggingFace diffusion models
- **transformers:** 5.3.0 — LLM/vision models
- **torchvision:** 0.25.0 — Image transforms
- **pillow:** 11.3.0 — Image manipulation
- **numpy/scipy:** Numerical computing

### Voice/TTS
- **ElevenLabs API:** George voice (JBFqnCBsd6RMkjVDRZzb)
- **Local TTS:** Piper or Coqui (not installed, can add)

### OpenAI Whisper — Transcription
- **Version:** 20250625 (installed April 2025)
- **Use for:** Auto-generating subtitles for Shorts

---

Add whatever helps you do your job. This is your cheat sheet.
