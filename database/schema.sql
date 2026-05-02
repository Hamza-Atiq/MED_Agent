-- MedAgent Database Schema
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS patients (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT,
  phone TEXT UNIQUE NOT NULL,
  whatsapp_id TEXT,
  city TEXT DEFAULT 'Lahore',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS doctors (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  specialty TEXT NOT NULL,
  phone TEXT NOT NULL,
  whatsapp_id TEXT,
  city TEXT NOT NULL,
  is_available BOOLEAN DEFAULT TRUE,
  rating FLOAT DEFAULT 5.0,
  total_cases INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS appointments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  patient_id UUID REFERENCES patients(id),
  doctor_id UUID REFERENCES doctors(id),
  problem_description TEXT,
  emergency_type TEXT,
  urgency_level TEXT,
  status TEXT DEFAULT 'pending',
  is_home_visit BOOLEAN DEFAULT TRUE,
  scheduled_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS activity_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  patient_id UUID REFERENCES patients(id),
  doctor_id UUID REFERENCES doctors(id),
  agent_used TEXT DEFAULT 'main_agent',
  emergency_type TEXT,
  urgency_level TEXT,
  patient_message TEXT,
  ai_response TEXT,
  doctor_notified BOOLEAN DEFAULT FALSE,
  -- XAI fields
  reasoning TEXT,
  key_symptoms JSONB DEFAULT '[]',
  confidence TEXT DEFAULT 'medium',
  triage_flags JSONB DEFAULT '[]',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Supabase Realtime for live dashboard (from Faheem)
ALTER PUBLICATION supabase_realtime ADD TABLE activity_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE appointments;
