const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export type AgentResponse = {
  response: string;
  emergency_type: string;
  urgency: string;
  doctor_assigned: string;
  disclaimer: string;
  reasoning: string;
  key_symptoms: string[];
  confidence: string;
  triage_flags: string[];
};

export async function sendMessage(message: string, phone = "demo-user", city = "Lahore"): Promise<AgentResponse> {
  const res = await fetch(`${BACKEND}/webhook`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, phone, city }),
  });
  if (!res.ok) throw new Error(`Backend error: ${res.status}`);
  return res.json();
}

export async function getDoctors() {
  const res = await fetch(`${BACKEND}/api/doctors`);
  if (!res.ok) throw new Error("Failed to fetch doctors");
  return res.json();
}

export async function getLogs(limit = 20) {
  const res = await fetch(`${BACKEND}/api/activity-logs?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch logs");
  return res.json();
}

export async function bookAppointment(data: {
  patient_phone: string;
  doctor_id: string;
  problem_description: string;
  emergency_type?: string;
  urgency_level?: string;
}) {
  const res = await fetch(`${BACKEND}/api/appointments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to book appointment");
  return res.json();
}
