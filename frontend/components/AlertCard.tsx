"use client";
import ReasoningCard from "./ReasoningCard";
import type { ActivityLog } from "@/lib/supabase";

type Props = {
  log: ActivityLog;
};

const URGENCY_CONFIG: Record<string, { color: string; dot: string; label: string }> = {
  critical: { color: "border-red-500",    dot: "bg-red-500",    label: "CRITICAL" },
  moderate: { color: "border-yellow-500", dot: "bg-yellow-500", label: "MODERATE" },
  low:      { color: "border-green-500",  dot: "bg-green-500",  label: "LOW" },
};

const TYPE_EMOJI: Record<string, string> = {
  cardiac: "🫀",
  trauma:  "🩹",
  neuro:   "🧠",
  general: "🏥",
};

function timeAgo(dateStr: string): string {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export default function AlertCard({ log }: Props) {
  const urgency = log.urgency_level?.toLowerCase() || "low";
  const cfg = URGENCY_CONFIG[urgency] || URGENCY_CONFIG.low;
  const typeEmoji = TYPE_EMOJI[log.emergency_type?.toLowerCase() || "general"] || "🏥";

  return (
    <div className={`bg-slate-800 rounded-xl border-l-4 ${cfg.color} p-4 space-y-2`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full ${cfg.dot} animate-pulse flex-shrink-0 mt-1`} />
          <div>
            <span className="font-bold text-white">
              {typeEmoji} {(log.emergency_type || "general").toUpperCase()}
            </span>
            <span className={`ml-2 text-xs font-semibold px-1.5 py-0.5 rounded ${cfg.dot} text-white`}>
              {cfg.label}
            </span>
          </div>
        </div>
        <span className="text-slate-500 text-xs whitespace-nowrap">{timeAgo(log.created_at)}</span>
      </div>

      {/* Patient info */}
      <div className="text-sm text-slate-400">
        <span className="font-medium text-slate-200">
          {log.patients?.name || log.patients?.phone || "Anonymous"}
        </span>
        {log.patients?.city && <span className="ml-1">· {log.patients.city}</span>}
      </div>

      {/* Patient message */}
      {log.patient_message && (
        <p className="text-slate-300 text-sm italic line-clamp-2">
          &ldquo;{log.patient_message}&rdquo;
        </p>
      )}

      {/* Doctor assigned */}
      {log.doctors && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-slate-500">Doctor:</span>
          <span className="text-white font-medium">
            {log.doctors.name}
          </span>
          <span className="text-slate-400">
            ({log.doctors.specialty}, {log.doctors.city})
          </span>
          {log.doctor_notified && (
            <span className="ml-auto text-green-400 text-xs">✅ Alert sent</span>
          )}
        </div>
      )}

      {/* XAI Reasoning */}
      {log.reasoning && (
        <ReasoningCard
          reasoning={log.reasoning}
          keySymptoms={log.key_symptoms || []}
          confidence={log.confidence || "low"}
          triageFlags={log.triage_flags || []}
          emergencyType={log.emergency_type || "general"}
          urgency={urgency}
        />
      )}
    </div>
  );
}
