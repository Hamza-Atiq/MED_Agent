"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

type Case = {
  id: string;
  emergency_type: string;
  urgency_level: string;
  ai_response: string;
  status: string;
  created_at: string;
  patients?: { name: string; phone: string; city: string };
};

type Doctor = { name: string; city: string; specialty: string };

const URGENCY_COLOR: Record<string, string> = {
  critical: "bg-red-900/50 border-red-700 text-red-300",
  moderate: "bg-yellow-900/50 border-yellow-700 text-yellow-300",
  low: "bg-green-900/50 border-green-700 text-green-300",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "🕐 Pending",
  in_progress: "🔵 In Progress",
  resolved: "✅ Resolved",
};

export default function DoctorCases() {
  const router = useRouter();
  const [cases, setCases] = useState<Case[]>([]);
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("doctor_token");
    if (!token) { router.push("/doctor/login"); return; }
    fetchCases(token);
  }, [router]);

  async function fetchCases(token: string) {
    try {
      const res = await fetch(`${API}/api/doctor/cases`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 401) { router.push("/doctor/login"); return; }
      const data = await res.json();
      setCases(data.cases || []);
      setDoctor(data.doctor || null);
    } catch {
      // keep showing whatever we have
    } finally {
      setLoading(false);
    }
  }

  async function updateStatus(caseId: string, status: string) {
    const token = localStorage.getItem("doctor_token");
    if (!token) return;
    setUpdating(caseId);
    try {
      await fetch(`${API}/api/doctor/cases/${caseId}/status`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      setCases((prev) => prev.map((c) => (c.id === caseId ? { ...c, status } : c)));
    } finally {
      setUpdating(null);
    }
  }

  function logout() {
    localStorage.removeItem("doctor_token");
    localStorage.removeItem("doctor_info");
    router.push("/doctor/login");
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <span className="text-2xl">👨‍⚕️</span>
          <div>
            <h1 className="font-bold text-lg">{doctor?.name || "Doctor Portal"}</h1>
            <p className="text-slate-400 text-xs">{doctor?.specialty} · {doctor?.city}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-blue-400 hover:text-blue-300 text-sm">Dashboard</Link>
          <button onClick={logout} className="text-slate-400 hover:text-red-400 text-sm transition-colors">
            Sign Out
          </button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-slate-300 text-sm uppercase tracking-wide">
            Your Assigned Cases ({cases.length})
          </h2>
          <button
            onClick={() => { const t = localStorage.getItem("doctor_token"); if (t) fetchCases(t); }}
            className="text-blue-400 hover:text-blue-300 text-sm"
          >
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="text-slate-500 text-center py-16 animate-pulse">Loading cases...</div>
        ) : cases.length === 0 ? (
          <div className="text-slate-500 text-center py-16">
            No cases assigned yet. Cases appear here when the AI dispatches you.
          </div>
        ) : (
          cases.map((c) => (
            <div key={c.id} className={`rounded-xl border p-4 space-y-3 ${URGENCY_COLOR[c.urgency_level] || "bg-slate-800 border-slate-700"}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm uppercase">{c.emergency_type}</span>
                  <span className="text-xs opacity-70">· {c.urgency_level}</span>
                </div>
                <span className="text-xs opacity-60">
                  {new Date(c.created_at).toLocaleString("en-PK", { hour: "2-digit", minute: "2-digit", month: "short", day: "numeric" })}
                </span>
              </div>

              {c.patients && (
                <div className="text-sm">
                  <span className="font-medium">{c.patients.name}</span>
                  <span className="opacity-70 ml-2">{c.patients.phone} · {c.patients.city}</span>
                </div>
              )}

              <p className="text-xs opacity-80 leading-relaxed line-clamp-3">{c.ai_response}</p>

              <div className="flex items-center gap-2 pt-1">
                <span className="text-xs opacity-70 mr-1">{STATUS_LABELS[c.status] || "🕐 Pending"}</span>
                {["pending", "in_progress", "resolved"].map((s) => (
                  <button
                    key={s}
                    disabled={c.status === s || updating === c.id}
                    onClick={() => updateStatus(c.id, s)}
                    className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors disabled:opacity-40 ${
                      c.status === s
                        ? "bg-white/20 text-white"
                        : "bg-white/10 hover:bg-white/20 text-white"
                    }`}
                  >
                    {s.replace("_", " ")}
                  </button>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
