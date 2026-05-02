"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import AlertCard from "@/components/AlertCard";
import { supabase, type ActivityLog, type Doctor } from "@/lib/supabase";
import { getLogs, getDoctors } from "@/lib/api";

const URGENCY_ORDER: Record<string, number> = { critical: 0, moderate: 1, low: 2 };

export default function Dashboard() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [liveCount, setLiveCount] = useState(0);

  useEffect(() => {
    async function load() {
      try {
        const [logData, docData] = await Promise.all([getLogs(30), getDoctors()]);
        setLogs(logData.logs || []);
        setDoctors(docData.doctors || []);
      } catch (e) {
        console.error("Failed to load dashboard data:", e);
      } finally {
        setLoading(false);
      }
    }
    load();

    // Supabase Realtime — primary live updates
    const channel = supabase
      .channel("activity_logs")
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "activity_logs" },
        (payload) => {
          setLogs((prev) => [payload.new as ActivityLog, ...prev]);
          setLiveCount((n) => n + 1);
        }
      )
      .subscribe();

    // Polling fallback — refreshes every 15s to catch missed realtime events
    const poll = setInterval(async () => {
      try {
        const [logData, docData] = await Promise.all([getLogs(30), getDoctors()]);
        setLogs(logData.logs || []);
        setDoctors(docData.doctors || []);
      } catch {
        // silently ignore — realtime may still be working
      }
    }, 15_000);

    return () => {
      supabase.removeChannel(channel);
      clearInterval(poll);
    };
  }, []);

  const filtered = logs
    .filter((l) => filter === "all" || l.emergency_type === filter)
    .sort((a, b) => (URGENCY_ORDER[a.urgency_level] ?? 2) - (URGENCY_ORDER[b.urgency_level] ?? 2));

  const criticalCount = logs.filter((l) => l.urgency_level === "critical").length;
  const moderateCount = logs.filter((l) => l.urgency_level === "moderate").length;

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📊</span>
          <div>
            <h1 className="font-bold text-xl">MedAgent Dashboard</h1>
            <p className="text-slate-400 text-xs">Live Emergency Response Monitor</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-sm">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-green-400 font-medium">Live</span>
            {liveCount > 0 && (
              <span className="bg-blue-600 text-white text-xs px-1.5 rounded-full ml-1">+{liveCount} new</span>
            )}
          </div>
          <Link href="/" className="text-blue-400 hover:text-blue-300 text-sm">
            ← Patient Chat
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Total Cases" value={logs.length} color="blue" />
          <StatCard label="Critical" value={criticalCount} color="red" />
          <StatCard label="Moderate" value={moderateCount} color="yellow" />
          <StatCard label="Doctors Available" value={doctors.filter((d) => d.is_available).length} color="green" />
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Cases panel */}
          <div className="md:col-span-2 space-y-4">
            {/* Filter tabs */}
            <div className="flex gap-2 flex-wrap">
              {["all", "cardiac", "trauma", "neuro", "respiratory", "gynae", "pediatric", "general"].map((t) => (
                <button
                  key={t}
                  onClick={() => setFilter(t)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    filter === t
                      ? "bg-blue-600 text-white"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }`}
                >
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </button>
              ))}
            </div>

            {loading ? (
              <div className="text-slate-500 text-center py-12 animate-pulse">Loading cases...</div>
            ) : filtered.length === 0 ? (
              <div className="text-slate-500 text-center py-12">
                No cases yet. Send a message on the patient chat to create one.
              </div>
            ) : (
              <div className="space-y-3">
                {filtered.map((log) => (
                  <AlertCard key={log.id} log={log} />
                ))}
              </div>
            )}
          </div>

          {/* Doctors panel */}
          <div className="space-y-3">
            <h2 className="font-semibold text-slate-300 text-sm uppercase tracking-wide">Doctors On Call</h2>
            {doctors.map((doc) => (
              <div key={doc.id} className="bg-slate-800 rounded-xl p-3 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-white text-sm">{doc.name}</span>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${
                      doc.is_available ? "bg-green-900 text-green-300" : "bg-slate-700 text-slate-400"
                    }`}
                  >
                    {doc.is_available ? "Available" : "Busy"}
                  </span>
                </div>
                <div className="text-slate-400 text-xs">
                  {doc.specialty} · {doc.city}
                </div>
                <div className="text-yellow-400 text-xs">★ {doc.rating}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const colors: Record<string, string> = {
    blue:   "text-blue-400",
    red:    "text-red-400",
    yellow: "text-yellow-400",
    green:  "text-green-400",
  };
  return (
    <div className="bg-slate-800 rounded-xl p-4">
      <p className="text-slate-400 text-xs uppercase tracking-wide">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${colors[color]}`}>{value}</p>
    </div>
  );
}
