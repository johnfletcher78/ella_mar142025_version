#!/usr/bin/env node
/**
 * Initialize Supabase memory table using direct REST API
 */

import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: join(__dirname, '.env') });

async function init() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_KEY;
  
  try {
    // Try direct REST call to create table
    const response = await fetch(`${url}/rest/v1/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
      },
      body: JSON.stringify({
        query: "CREATE TABLE IF NOT EXISTS memories (id uuid DEFAULT gen_random_uuid() PRIMARY KEY, summary text NOT NULL, details jsonb DEFAULT '{}', created_at timestamptz DEFAULT now())"
      })
    });

    console.log(JSON.stringify({
      status: response.status,
      message: 'Attempt completed',
      note: 'If table creation failed, run SQL manually in Supabase dashboard'
    }));
  } catch (err) {
    console.error(JSON.stringify({ error: err.message }));
  }
}

init();
