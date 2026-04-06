#!/usr/bin/env python3
"""
Test Supabase connection and schema.
"""
import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv('/home/bull/ella/.env')

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')

print(f"URL: {url}")
print(f"Key present: {bool(key)}")

client: Client = create_client(url, key)

# Try to list tables (PostgREST metadata)
try:
    tables = client.from_('').select('*').execute()
    print("Tables metadata:", json.dumps(tables.data, indent=2)[:500])
except Exception as e:
    print(f"Error getting tables: {e}")

# Try to check if agent_memory table exists with a simple query
try:
    # Try to get table schema
    result = client.table('agent_memory').select('id').limit(1).execute()
    print(f"agent_memory exists with {len(result.data)} rows")
    if result.data:
        print("Sample row:", result.data[0])
except Exception as e:
    print(f"agent_memory query error: {e}")
    
# Try to create a simple test table if agent_memory doesn't exist
try:
    test_data = {
        'agent_name': 'ella_test',
        'content': 'Test connection from Ella',
        'memory_type': 'test'
    }
    result = client.table('agent_memory').insert(test_data).execute()
    print(f"Insert successful! ID: {result.data[0]['id'] if result.data else 'unknown'}")
except Exception as e:
    print(f"Insert failed: {e}")
    print("\nConclusion: Schema needs initialization.")
    print(f"Run SQL from: /home/bull/ella/brain/supabase_schema.sql")
    print(f"at: {url}/sql")