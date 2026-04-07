#!/bin/bash
# Discord to Supabase Logger
# Logs webhook messages to shared memory

WEBHOOK_URL="https://discord.com/api/webhooks/1490745327320436927/So7jSW9o366VNbbCXfN-WkAe_5TQBN4xLpzdYJZ1f9ilCcXXLUS3GwlYCnED8QTYnUCX"
DISCORD_CHANNEL="Bulls_AI_Lab"

echo "🔄 Discord-Supabase Sync"
echo "========================"

# This script would be triggered by Discord webhook events
# For now, we'll log manual messages

if [ -z "$1" ]; then
  echo "Usage: $0 'Your message here'"
  exit 1
fi

MESSAGE="$1"
AGENT="ella"

# Send to Discord
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"${MESSAGE}\",\"username\":\"${AGENT}\"}" \
  "$WEBHOOK_URL" > /dev/null

# Log to Supabase (via Python script)
python3 << EOF
import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('/home/bull/ella/.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

data = {
    'agent_id': '${AGENT}',
    'session_key': 'discord_${DISCORD_CHANNEL}',
    'content': '${MESSAGE}',
    'metadata': {
        'source': 'discord_webhook',
        'channel': '${DISCORD_CHANNEL}',
        'timestamp': datetime.now().isoformat(),
        'webhook': True
    }
}

client.table('agent_memory').insert(data).execute()
print('✅ Message logged to Supabase')
EOF

echo "✅ Message sent to Discord and logged to Supabase"