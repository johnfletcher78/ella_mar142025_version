## [2026-03-19] - Node.js - Loading .env files in skills
Problem: process.env variables not available when running skill directly with node
Root Cause: .env file is not automatically loaded by Node.js
Solution: Manually parse .env file with fs.readFileSync or use dotenv package
Rule: Always explicitly load .env at the top of any skill run.mjs that needs environment variables

## [2026-03-19] - OpenClaw - No exec subcommand
Problem: openclaw exec is not a valid command
Root Cause: exec is a gateway tool not a CLI subcommand
Solution: Use curl to hit the remote gateway health endpoint instead
Rule: Never use openclaw exec from the CLI — use curl for remote health checks
