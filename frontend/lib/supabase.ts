import { createClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(url, key);

export type ActivityLog = {
  id: string;
  created_at: string;
  patient_message: string;
  ai_response: string;
  emergency_type: string;
  urgency_level: string;
  reasoning: string;
  key_symptoms: string[];
  confidence: string;
  triage_flags: string[];
  doctor_notified: boolean;
  patients?: { name: string; phone: string; city: string } | null;
  doctors?: { name: string; specialty: string; city: string } | null;
};

export type Doctor = {
  id: string;
  name: string;
  specialty: string;
  city: string;
  phone: string;
  is_available: boolean;
  rating: number;
  total_cases: number;
};
