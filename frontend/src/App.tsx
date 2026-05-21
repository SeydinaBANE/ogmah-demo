import { useState } from "react";
import Dashboard from "./components/Dashboard";
import AnomalyPanel from "./components/AnomalyPanel";
import ForecastChart from "./components/ForecastChart";
import ChatInterface from "./components/ChatInterface";

type Tab = "dashboard" | "anomalies" | "forecast" | "chat";

const TABS: { id: Tab; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "anomalies", label: "Anomalies" },
  { id: "forecast", label: "Prévisions" },
  { id: "chat", label: "Assistant IA" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("dashboard");

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm font-bold">O</span>
          </div>
          <span className="text-lg font-semibold text-gray-900">OgmahDemo</span>
          <span className="text-sm text-gray-400 font-normal">Restaurant AI</span>
        </div>
        <nav className="flex gap-1 ml-6">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === t.id
                  ? "bg-brand-50 text-brand-700"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="flex-1 p-6">
        {activeTab === "dashboard" && <Dashboard />}
        {activeTab === "anomalies" && <AnomalyPanel />}
        {activeTab === "forecast" && <ForecastChart />}
        {activeTab === "chat" && <ChatInterface />}
      </main>
    </div>
  );
}
