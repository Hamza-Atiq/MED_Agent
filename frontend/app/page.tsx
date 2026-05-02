import ChatWidget from "@/components/ChatWidget";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f0f2f5] flex flex-col">
      {/* WhatsApp-style green header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-[#075E54]">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🏥</span>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">MedAgent</h1>
            <p className="text-green-200 text-xs">AI Emergency Healthcare · Online</p>
          </div>
        </div>
        <Link
          href="/dashboard"
          className="text-green-200 hover:text-white text-sm font-medium transition-colors"
        >
          Dashboard →
        </Link>
      </header>

      {/* Chat — max width keeps it phone-like on desktop */}
      <div className="flex-1 flex flex-col max-w-2xl w-full mx-auto shadow-sm">
        <ChatWidget />
      </div>
    </div>
  );
}
