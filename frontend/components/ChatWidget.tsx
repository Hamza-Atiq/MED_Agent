"use client";
import { useState, useRef, useEffect, useCallback } from "react";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
const STORAGE_KEY = "medagent_chat_v1";

type TriageMeta = {
  emergency_type: string;
  urgency: string;
  doctor_assigned: string;
  reasoning: string;
  key_symptoms: string[];
  confidence: string;
};

type Message = {
  id: string;
  role: "patient" | "agent";
  text: string;
  timestamp: Date;
  meta?: TriageMeta;
};

const URGENCY_BADGE: Record<string, string> = {
  critical: "bg-red-100 text-red-700 border-red-200",
  moderate: "bg-amber-100 text-amber-700 border-amber-200",
  low:      "bg-green-100 text-green-700 border-green-200",
};

const URGENCY_EMOJI: Record<string, string> = {
  critical: "🔴", moderate: "🟡", low: "🟢",
};

const TYPE_EMOJI: Record<string, string> = {
  cardiac: "🫀", trauma: "🩹", neuro: "🧠",
  respiratory: "🫁", gynae: "👩‍⚕️", pediatric: "👶", general: "🏥",
};

const WELCOME: Message = {
  id: "0",
  role: "agent",
  text: "Assalam o Alaikum! I'm MedAgent — your AI emergency medical assistant.\n\nPlease describe the emergency and I will immediately guide you and connect you with a doctor. 🏥",
  timestamp: new Date(),
};

function reviveMessages(raw: unknown): Message[] {
  if (!Array.isArray(raw) || raw.length === 0) return [WELCOME];
  return raw.map((m: Record<string, unknown>) => ({ ...m, timestamp: new Date(m.timestamp as string) })) as Message[];
}

export default function ChatWidget() {
  const [hydrated, setHydrated] = useState(false);
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("Patient");
  const [city, setCity] = useState("");
  const [phone] = useState(() => {
    if (typeof window === "undefined") return "demo-ssr";
    const saved = localStorage.getItem(STORAGE_KEY + "_phone");
    if (saved) return saved;
    const id = `demo-${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem(STORAGE_KEY + "_phone", id);
    return id;
  });
  const [history, setHistory] = useState<{ role: string; content: string }[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load persisted state from localStorage after hydration
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const saved = JSON.parse(raw);
        setMessages(reviveMessages(saved.messages));
        setName(saved.name || "Patient");
        setCity(saved.city || "");
        setHistory(saved.history || []);
      }
    } catch { /* ignore corrupt storage */ }
    setHydrated(true);
  }, []);

  // Persist to localStorage whenever messages or profile change
  const saveToStorage = useCallback((
    msgs: Message[],
    n: string,
    c: string,
    hist: { role: string; content: string }[],
  ) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ messages: msgs, name: n, city: c, history: hist }));
    } catch { /* quota exceeded — ignore */ }
  }, []);

  useEffect(() => {
    if (hydrated) saveToStorage(messages, name, city, history);
  }, [messages, name, city, history, hydrated, saveToStorage]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;
    if (!city.trim()) {
      setMessages((m) => [...m, {
        id: Date.now().toString(),
        role: "agent",
        text: "Please enter your city above so I can assign the nearest doctor to you.",
        timestamp: new Date(),
      }]);
      return;
    }

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "patient",
      text,
      timestamp: new Date(),
    };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    const newHistory = [...history, { role: "user", content: text }];

    try {
      const res = await fetch(`${BACKEND}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, phone, name, city, history: newHistory }),
      });
      if (!res.ok) throw new Error("API error");
      const data = await res.json();

      const fullText = data.response || data.greeting || "Processing your emergency...";
      const agentMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "agent",
        text: fullText,
        timestamp: new Date(),
        meta: data.emergency_type ? {
          emergency_type: data.emergency_type,
          urgency: data.urgency,
          doctor_assigned: data.doctor_assigned,
          reasoning: data.reasoning,
          key_symptoms: data.key_symptoms || [],
          confidence: data.confidence,
        } : undefined,
      };
      setMessages((m) => [...m, agentMsg]);
      setHistory([...newHistory, { role: "assistant", content: fullText }]);
    } catch {
      setMessages((m) => [...m, {
        id: (Date.now() + 1).toString(),
        role: "agent",
        text: "⚠️ Connection error. If this is an emergency, call 1122 (Rescue) or 115 (Edhi) immediately.",
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full bg-[#f0f2f5]">
      {/* Patient info bar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2 flex gap-3 items-center flex-wrap">
        <span className="text-xs text-gray-500 font-medium">Your info:</span>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border border-gray-200 rounded-lg px-2 py-1 text-xs w-32 focus:outline-none focus:border-green-400"
          placeholder="Your name"
        />
        <input
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className={`border rounded-lg px-2 py-1 text-xs w-28 focus:outline-none focus:border-green-400 ${!city ? "border-amber-300 bg-amber-50" : "border-gray-200"}`}
          placeholder="Your city ⚠️"
        />
        {messages.length > 1 && (
          <button
            onClick={() => {
              setMessages([WELCOME]);
              setHistory([]);
              localStorage.removeItem(STORAGE_KEY);
            }}
            className="ml-auto text-[10px] text-gray-400 hover:text-red-500 transition-colors"
          >
            Clear chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === "patient" ? "justify-end" : "justify-start"}`}>
            <div className="max-w-[85%] space-y-1.5">
              {/* Chat bubble — WhatsApp style */}
              <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-sm ${
                msg.role === "patient"
                  ? "bg-[#dcf8c6] text-gray-900 rounded-br-none"
                  : "bg-white text-gray-900 rounded-bl-none border border-gray-100"
              }`}>
                {msg.role === "agent" && (
                  <p className="text-xs font-bold text-green-600 mb-1">🏥 MedAgent</p>
                )}
                {msg.text}
              </div>

              {/* Triage badge + doctor card */}
              {msg.meta && (
                <div className="space-y-1.5">
                  <div className="flex flex-wrap gap-1.5 text-xs">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border font-semibold ${URGENCY_BADGE[msg.meta.urgency] || "bg-gray-100 text-gray-600"}`}>
                      {URGENCY_EMOJI[msg.meta.urgency]} {TYPE_EMOJI[msg.meta.emergency_type] || "🏥"} {msg.meta.emergency_type.toUpperCase()} · {msg.meta.urgency.toUpperCase()}
                    </span>
                  </div>

                  {/* Doctor card */}
                  {msg.meta.doctor_assigned && msg.meta.doctor_assigned !== "Searching..." && (
                    <div className="bg-[#edf7f2] border border-[#b7e8c8] rounded-xl px-3 py-2 text-xs">
                      <p className="font-bold text-green-700 mb-0.5">✅ Doctor Assigned</p>
                      <p className="text-gray-700">{msg.meta.doctor_assigned}</p>
                    </div>
                  )}

                  {/* XAI Reasoning — our unique feature */}
                  {msg.meta.reasoning && (
                    <details className="bg-white border border-gray-100 rounded-xl text-xs shadow-sm">
                      <summary className="cursor-pointer px-3 py-2 text-blue-600 font-semibold select-none">
                        🧠 Why this classification?
                      </summary>
                      <div className="px-3 pb-3 pt-1 space-y-2">
                        <p className="text-gray-600 leading-relaxed">{msg.meta.reasoning}</p>
                        {msg.meta.key_symptoms.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {msg.meta.key_symptoms.map((s) => (
                              <span key={s} className="bg-red-50 text-red-600 border border-red-100 px-1.5 py-0.5 rounded-full">
                                ✓ {s}
                              </span>
                            ))}
                          </div>
                        )}
                        <p className="text-gray-400">
                          Confidence: <span className="font-semibold text-gray-600">{msg.meta.confidence}</span>
                        </p>
                      </div>
                    </details>
                  )}
                </div>
              )}

              <p className="text-[10px] text-gray-400 px-1" suppressHydrationWarning>
                {msg.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {/* Loading dots — Faheem's style */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl rounded-bl-none px-4 py-3 shadow-sm border border-gray-100">
              <div className="flex gap-1 items-center">
                {[0, 150, 300].map((delay) => (
                  <div key={delay} className="w-2 h-2 bg-green-500 rounded-full animate-bounce"
                    style={{ animationDelay: `${delay}ms` }} />
                ))}
                <span className="text-xs text-gray-400 ml-2">AI agents working...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 py-3">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Describe the emergency..."
            disabled={loading}
            className="flex-1 bg-[#f0f2f5] text-gray-900 placeholder-gray-400 px-4 py-2.5 rounded-full text-sm outline-none focus:ring-2 focus:ring-green-400 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-green-500 hover:bg-green-600 disabled:opacity-40 text-white px-5 py-2.5 rounded-full font-bold text-sm transition-colors"
          >
            Send
          </button>
        </div>
        <p className="text-[10px] text-gray-400 mt-1.5 text-center">
          ⚠️ For informational use only · In real emergency call 1122 or 115
        </p>
      </div>
    </div>
  );
}
