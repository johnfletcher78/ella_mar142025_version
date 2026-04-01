#!/usr/bin/env node
/**
 * agent-memory-supabase
 * Store and retrieve long-term memories from Supabase
 * 
 * Usage:
 *   node run.mjs loadMemories
 *   node run.mjs logMemory "Summary text" '{"key":"value"}'
 */

import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env from skill directory
dotenv.config({ path: join(__dirname, '.env') });

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
const TABLE_NAME = process.env.MEMORY_TABLE || 'memories';

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error(JSON.stringify({
    error: 'Missing environment variables',
    details: 'SUPABASE_URL and SUPABASE_KEY must be set in .env'
  }));
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function loadMemories() {
  try {
    const { data, error } = await supabase
      .from(TABLE_NAME)
      .select('id, summary, details, created_at')
      .order('created_at', { ascending: false })
      .limit(50);

    if (error) throw error;

    console.log(JSON.stringify({
      success: true,
      count: data?.length || 0,
      memories: data || []
    }));
  } catch (err) {
    console.error(JSON.stringify({
      error: 'Failed to load memories',
      details: err.message
    }));
    process.exit(1);
  }
}

async function logMemory(summary, detailsJson = '{}') {
  if (!summary) {
    console.error(JSON.stringify({
      error: 'Missing required argument',
      details: 'Summary is required for logMemory action'
    }));
    process.exit(1);
  }

  let details = {};
  try {
    details = JSON.parse(detailsJson);
  } catch {
    // If not valid JSON, store as string in a details field
    details = { note: detailsJson };
  }

  try {
    const { data, error } = await supabase
      .from(TABLE_NAME)
      .insert([{ summary, details }])
      .select()
      .single();

    if (error) throw error;

    console.log(JSON.stringify({
      success: true,
      id: data.id,
      summary: data.summary,
      created_at: data.created_at
    }));
  } catch (err) {
    console.error(JSON.stringify({
      error: 'Failed to log memory',
      details: err.message
    }));
    process.exit(1);
  }
}

// Main CLI handler
const [action, ...args] = process.argv.slice(2);

switch (action) {
  case 'loadMemories':
    await loadMemories();
    break;
    
  case 'logMemory':
    const [summary, detailsJson = '{}'] = args;
    await logMemory(summary, detailsJson);
    break;
    
  default:
    console.error(JSON.stringify({
      error: 'Unknown action',
      details: `Action "${action}" not recognized. Use: loadMemories | logMemory`,
      usage: 'node run.mjs loadMemories\nnode run.mjs logMemory "Summary" \'{...}\''
    }));
    process.exit(1);
}
