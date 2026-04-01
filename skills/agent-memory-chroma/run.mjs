#!/usr/bin/env node
/**
 * agent-memory-chroma
 * Store and retrieve memories with semantic search via Chroma
 * 
 * Usage:
 *   node run.mjs loadMemories
 *   node run.mjs logMemory "Summary" '{"key":"value"}'
 */

import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: join(__dirname, '.env') });

const CHROMA_URL = process.env.CHROMA_URL || 'http://localhost:8000';
const COLLECTION_NAME = process.env.CHROMA_COLLECTION || 'ella_memories';
const TENANT = 'default';
const DATABASE = 'default';

// Collection UUID - will be discovered
let collectionId = null;

async function chromaFetch(path, method = 'GET', body = null) {
  const url = `${CHROMA_URL}${path}`;
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) options.body = JSON.stringify(body);
  
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Chroma ${response.status}: ${text}`);
  }
  return response.status === 204 ? null : await response.json();
}

async function getCollectionId() {
  if (collectionId) return collectionId;
  
  const collections = await chromaFetch(`/api/v2/tenants/${TENANT}/databases/${DATABASE}/collections`);
  const coll = collections.find(c => c.name === COLLECTION_NAME);
  if (coll) {
    collectionId = coll.id;
    return coll.id;
  }
  
  // Create collection
  const newColl = await chromaFetch(`/api/v2/tenants/${TENANT}/databases/${DATABASE}/collections`, 'POST', {
    name: COLLECTION_NAME,
    configuration: {}
  });
  collectionId = newColl.id;
  return collectionId;
}

// Simple hash-based embedding
function getEmbedding(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  
  const embedding = [];
  const rng = () => {
    hash = (hash * 1664525 + 1013904223) % 4294967296;
    return (hash / 4294967296) * 2 - 1;
  };
  
  for (let i = 0; i < 384; i++) {
    embedding.push(rng());
  }
  return embedding;
}

async function loadMemories() {
  try {
    const id = await getCollectionId();
    
    const response = await chromaFetch(`/api/v2/tenants/${TENANT}/databases/${DATABASE}/collections/${id}/get`, 'POST', {
      limit: 50
    });
    
    const memories = (response.ids || []).map((memId, i) => ({
      id: memId,
      summary: response.documents?.[i] || '',
      details: JSON.parse(response.metadatas?.[i]?.details || '{}'),
      created_at: response.metadatas?.[i]?.created_at || new Date().toISOString()
    }));
    
    console.log(JSON.stringify({
      success: true,
      count: memories.length,
      memories
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
      error: 'Missing summary',
      details: 'Summary is required'
    }));
    process.exit(1);
  }

  try {
    const id = await getCollectionId();
    const embedding = getEmbedding(summary);
    
    let details = {};
    try { details = JSON.parse(detailsJson); } catch { details = { note: detailsJson }; }
    
    const memId = crypto.randomUUID();
    const now = new Date().toISOString();
    
    await chromaFetch(`/api/v2/tenants/${TENANT}/databases/${DATABASE}/collections/${id}/upsert`, 'POST', {
      ids: [memId],
      embeddings: [embedding],
      documents: [summary],
      metadatas: [{ details: JSON.stringify(details), created_at: now }]
    });

    console.log(JSON.stringify({
      success: true,
      id: memId,
      summary,
      created_at: now
    }));
  } catch (err) {
    console.error(JSON.stringify({
      error: 'Failed to log memory',
      details: err.message
    }));
    process.exit(1);
  }
}

const [action, ...args] = process.argv.slice(2);

switch (action) {
  case 'loadMemories':
    await loadMemories();
    break;
  case 'logMemory':
    await logMemory(args[0], args[1] || '{}');
    break;
  default:
    console.error(JSON.stringify({
      error: 'Unknown action',
      usage: 'node run.mjs loadMemories | node run.mjs logMemory "summary" \'{...}\''
    }));
    process.exit(1);
}
