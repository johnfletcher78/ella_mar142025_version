# AGENTS.md - System Architecture

## Overview
- **Ella** – local assistant running on your machine (Telegram interface, Guardian health‑monitor, orchestrator). 
- **Atlas** – remote VPS profile (`--profile atlas`). It hosts the **brain** for the agency pipeline and owns all sub‑agents that build and deploy client websites.
- **Guardian** – lightweight local agent that watches the Atlas connection, runs health checks, and sends alerts to you via Telegram.

## Atlas pipeline agents (live on the VPS)
1. `channel-normalizer` – normalises raw intake data from any source into the canonical `brief.json` format.
2. `client-intake-bot` – validates the normalized brief, asks follow‑up questions, persists partial sessions in `intake_sessions/`.
3. `design-strategist` – selects templates, defines layout, colour system, typography, CTA strategy.
4. `content-writer` – generates SEO‑optimized copy, meta tags, blog outlines.
5. `hugo-builder` – builds the static site with Hugo (or another generator) and produces a zip archive.
6. `qa-bot` – runs Lighthouse, checks mobile responsiveness, form submission, page‑speed, returns pass/fail report.
7. `site-admin` – SCP/SSH deploys the zip to the VPS, configures Nginx, SSL, DNS, backups, connects form data to the client CRM.
8. `mission-control` – top‑level orchestrator on Atlas that strings the above agents together, validates the live site, and reports back to Ella.

## Communication flow
```
User → Ella (Telegram) → Atlas (remote profile) → Pipeline agents → Atlas → Ella → User
```

## Roles summary
- **Ella**: front‑end, user interaction, health monitoring, triggers Atlas pipelines.
- **Atlas**: execution environment for all heavy‑weight website‑building agents.
- **Guardian**: watches the link between Ella and Atlas, alerts on failures.
