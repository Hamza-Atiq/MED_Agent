"use client";
import { useState } from "react";

type Props = {
  reasoning: string;
  keySymptoms: string[];
  confidence: string;
  triageFlags: string[];
  emergencyType: string;
  urgency: string;
};

const CONFIDENCE_COLOR: Record<string, string> = {
  high: "text-green-400",
  medium: "text-yellow-400",
  low: "text-orange-400",
};

const FLAG_LABELS: Record<string, string> = {
  chest_pain_keyword: "chest pain",
  multiple_symptoms: "multiple symptoms",
  urgency_escalated: "urgency escalated",
  cardiac_keyword: "cardiac keyword",
  trauma_keyword: "trauma keyword",
  neuro_keyword: "neuro keyword",
  pediatric_mention: "pediatric",
  elderly_mention: "elderly",
  fallback_used: "fallback",
  system_error: "system error",
  empty_message: "empty message",
  no_keywords: "no keywords",
};

export default function ReasoningCard({ reasoning, keySymptoms, confidence, triageFlags, emergencyType, urgency }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-2 border border-slate-600 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 py-2 bg-slate-700 hover:bg-slate-600 transition-colors text-sm"
      >
        <span className="flex items-center gap-2 font-medium text-blue-300">
          <span>🧠</span> AI Reasoning
        </span>
        <span className="text-slate-400 text-xs">{open ? "▲ collapse" : "▼ expand"}</span>
      </button>

      {open && (
        <div className="px-3 py-3 bg-slate-800 space-y-3 text-sm">
          <p className="text-slate-300 leading-relaxed">{reasoning}</p>

          {keySymptoms.length > 0 && (
            <div>
              <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">Detected symptoms</p>
              <div className="flex flex-wrap gap-1">
                {keySymptoms.map((s) => (
                  <span key={s} className="bg-red-900/50 text-red-300 px-2 py-0.5 rounded text-xs">
                    ✓ {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {triageFlags.filter(f => f !== "fallback_used" && f !== "system_error").length > 0 && (
            <div>
              <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">Triage signals</p>
              <div className="flex flex-wrap gap-1">
                {triageFlags.map((f) => (
                  <span key={f} className="bg-slate-700 text-slate-300 px-2 py-0.5 rounded text-xs">
                    {FLAG_LABELS[f] || f}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs pt-1 border-t border-slate-700">
            <span className="text-slate-500">Confidence:</span>
            <span className={`font-semibold uppercase ${CONFIDENCE_COLOR[confidence] || "text-slate-300"}`}>
              {confidence}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
