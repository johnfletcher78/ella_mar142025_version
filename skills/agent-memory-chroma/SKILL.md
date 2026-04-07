# agent-memory-chroma

Semantic memory storage using Chroma DB with embeddings.

## Usage

Load recent memories (all):
```yaml
tool: agent-memory-chroma
action: loadMemories
```

Semantic search:
```yaml
tool: agent-memory-chroma
action: loadMemories
query: "client website project"
n: 5
```

Log a new memory:
```yaml
tool: agent-memory-chroma
action: logMemory
summary: "Client approved the design"
details: '{"client": "Acme Corp", "decision": "approved"}'
```

## Environment Variables

Required in `.env` file:
- `CHROMA_URL` — Chroma server URL (default: `http://localhost:8000`)
- `CHROMA_COLLECTION` — Collection name (default: `ella_memories`)
- `OPENROUTER_API_KEY` — For embeddings (optional, uses random fallback if not set)

## Docker Setup

```bash
cd ~/.openclaw/workspace
docker run -d --name ella-chroma -p 8000:8000 \
  -v ~/.openclaw/workspace/chroma_data:/chroma/chroma \
  chromadb/chroma:latest
```

## CLI Usage

```bash
# Load memories
openclaw skill run agent-memory-chroma loadMemories

# Semantic search
openclaw skill run agent-memory-chroma loadMemories "website project" 5

# Log memory
openclaw skill run agent-memory-chroma logMemory "Summary" --details '{...}'
```

## How It Works

1. Text → Embeddings (via OpenRouter or local fallback)
2. Embeddings + metadata → Chroma DB
3. Semantic search → finds similar meanings, not just words

## Output Format

All responses are JSON:
- `loadMemories`: `{ success: true, count: N, memories: [...] }`
- `logMemory`: `{ success: true, id: "uuid", summary: "...", created_at: "..." }`
- Errors: `{ error: "...", details: "..." }`
