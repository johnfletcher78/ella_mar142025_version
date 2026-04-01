# TOOLS.md - Ella Local Notes

## Current Machine
- Host: bulls-AI-PC (Ubuntu)
- GPU: Nvidia RTX 4080
- User: bull
- Workspace: ~/.openclaw/workspace
- Model: ollama/gpt-oss:120b-cloud (local GPU‑accelerated)
- Always use python3, never python

## Atlas VPS
- Host: srv1365311
- IP: 187.77.20.204
- User: root
- SSH Key: ~/.ssh/vps_key

## Local Machine Details (replaces old Atlas VPS info)
- This is a local development machine, not a remote VPS.
- No SSH key or remote IP is needed for primary operations.
- OpenClaw runs directly in the local environment.

## Sites (running on this machine)
- Preview server: port 8095 (served locally)
- mission-control, beccas-closet, fresh-and-clean-auto-detail
- Traefik (local) – optional reverse‑proxy for preview URLs

## Rules
- Never use openrouter/auto
- Always use python3 not python
- Do not take irreversible actions without confirmation
- Do not expose credentials in chat
