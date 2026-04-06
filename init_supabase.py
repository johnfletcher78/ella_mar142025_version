#!/usr/bin/env python3
"""
Initialize the Supabase schema for Ella/Kai shared brain.
"""
import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/bull/ella/.env')

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')

if not url or not key:
    print("Error: Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
    sys.exit(1)

# Read schema
schema_path = '/home/bull/ella/brain/supabase_schema.sql'
with open(schema_path, 'r') as f:
    sql = f.read()

print(f"Connecting to Supabase...")
client = create_client(url, key)

print(f"Executing schema SQL...")
try:
    result = client.rpc('exec_sql', {'sql': sql}).execute()
    print("Schema created successfully!")
except Exception as e:
    print(f"Error executing SQL: {e}")
    print("\nTrying alternative method...")
    
    # Try to execute SQL directly if rpc not available
    # This might require SQL Editor permissions
    print("Schema needs to be run manually in Supabase SQL Editor:")
    print(f"URL: {url}/sql")
    print("\nCopy the SQL from:")
    print(f"  {schema_path}")