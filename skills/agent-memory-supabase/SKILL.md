# agent-memory-supabase

Store and retrieve long-term memories from Supabase.

## Usage

Load recent memories into context:
```yaml
tool: agent-memory-supabase
action: loadMemories
```

Log a new memory:
```yaml
tool: agent-memory-supabase
action: logMemory
summary: "Client approved the design"
details: '{"client": "Acme Corp", "decision": "approved"}'
```

## Environment Variables

Required in `.env` file:
- `SUPABASE_URL` — Your Supabase project URL (e.g., `https://xyz123.supabase.co`)
- `SUPABASE_KEY` — Your Supabase anon key or service role key
- `MEMORY_TABLE` — Table name (default: `memories`)

## Setup

1. Create the table in Supabase SQL Editor:
```sql
create table memories (
  id uuid default gen_random_uuid() primary key,
  summary text not null,
  details jsonb default '{}',
  created_at timestamptz default now()
);

-- Enable RLS and create policy (optional but recommended)
alter table memories enable row level security;
```

2. Install dependencies:
```bash
cd ~/.openclaw/workspace/skills/agent-memory-supabase
npm install @supabase/supabase-js dotenv
```

## CLI Usage

```bash
# Load memories
openclaw skill run agent-memory-supabase loadMemories

# Log a memory
openclaw skill run agent-memory-supabase logMemory "Summary here" --details '{"key":"value"}'
```

## Output Format

All responses are JSON:
- `loadMemories`: `{ success: true, count: N, memories: [...] }`
- `logMemory`: `{ success: true, id: "uuid", summary: "...", created_at: "..." }`
- Errors: `{ error: "...", details: "..." }`
