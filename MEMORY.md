# Ella — Memory Index

Long-term memory lives in Supabase (agent_memory table, agent_name='ella').
Daily notes live in memory/ folder below.

## Quick Facts
- First came online: 2026-04-05
- Kai's VPS: 104.238.172.231
- Shared brain: jnaifrwipyjggpnntkvk.supabase.co
- Brain scripts: /home/bull/ella/brain/

## Recent Milestones
- 2026-04-05: Ella rebuilt with shared brain architecture. Gateway fixed (port 18790), models configured, Supabase brain scripts created.
- 2026-04-05 (evening): Reconnected with Bull, confirmed identity. Supabase schema needs initialization for shared memory with Kai.
- 2026-04-06 (early AM): Switched primary model to Kimi 2.5 cloud. Coder subagent remains deepseek-v3.2:cloud.

## Notes
- Daily memory files: memory/YYYY-MM-DD.md
- Check Supabase for cross-session and cross-agent memory
- Using existing Supabase schema (Kai's setup) - do NOT modify schema
- Credentials at /home/bull/ella/.env
- Voice: ElevenLabs George (JBFqnCBsd6RMkjVDRZzb)
- Primary model: ollama/kimi-k2.5:cloud
- Coder subagent: ollama/deepseek-v3.2:cloud

## Local AI Tools Available
- **ComfyUI** — `/home/bull/ComfyUI` — ComfyUI node-based AI generation
  - SDXL Base checkpoint (6.5GB) installed
  - Can generate images, extend to video with SVD/AnimateDiff models
  - Python 3.11+ with torch 2.10, diffusers, transformers
- **FFmpeg** — `/home/bull/.local/bin/ffmpeg` — Video processing
- **Python Stack** — numpy, scipy, pillow, torch, diffusers, transformers
- **Missing for Full Pipeline** — MoviePy (install: `pip3 install moviepy`), OpenAI Whisper
