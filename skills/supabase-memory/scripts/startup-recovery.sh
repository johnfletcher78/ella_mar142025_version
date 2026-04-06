#!/bin/bash
# Ella Startup Recovery Script
# Runs on session start to recover context from Supabase

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$HOME/ella/.env"

echo "🧠 Ella Memory Recovery"
echo "======================"
echo ""

# Check if Supabase is configured
if [ ! -f "$ENV_FILE" ]; then
 echo "⚠️ Supabase not configured. Skipping memory recovery."
 exit 0
fi

# Source the .env file
set -a
source "$ENV_FILE"
set +a

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
 echo "⚠️ Supabase credentials incomplete"
 exit 0
fi

echo "✅ Supabase configured: $SUPABASE_URL"
echo ""

# Run recovery
cd "$SCRIPT_DIR/.."
node -e "
require('dotenv').config({ path: '$ENV_FILE' });
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

async function recover() {
 try {
 const { data: memories, error } = await supabase
 .from('agent_memory')
 .select('*')
 .order('created_at', { ascending: false })
 .limit(10);

 if (error) throw error;

 if (memories && memories.length > 0) {
 console.log('📚 Retrieved', memories.length, 'recent memories');
 memories.forEach(m => {
 console.log(' -', m.content?.substring(0, 60) + '...');
 });
 } else {
 console.log('📚 No recent memories found');
 }

 console.log('');
 console.log('✅ Recovery complete.');
 } catch (err) {
 console.log('❌ Error:', err.message);
 }
}

recover();
"