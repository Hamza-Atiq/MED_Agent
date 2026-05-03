-- Run this ONCE in Supabase SQL Editor
-- Adds WhatsApp conversation sessions table

CREATE TABLE IF NOT EXISTS sessions (
  phone       TEXT PRIMARY KEY,
  name        TEXT DEFAULT 'Patient',
  city        TEXT DEFAULT '',
  state       TEXT DEFAULT 'new',   -- new | ask_intake | active
  first_msg   TEXT DEFAULT '',      -- stores original message during intake
  history     JSONB DEFAULT '[]',   -- last 12 messages [{role, content}]
  updated_at  TIMESTAMP DEFAULT NOW()
);

-- Allow full access (backend reads and writes)
ALTER TABLE sessions DISABLE ROW LEVEL SECURITY;
