import { useRef, useState } from "react";
import { postJSON } from "../api/client";
import { v4 as uuidv4 } from "uuid";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTIONS = [
  "Quelle est notre marge moyenne ce mois-ci ?",
  "Quelles recettes ont un food cost > 30% ?",
  "Y a-t-il des anomalies d'achat cette semaine ?",
  "Quel est notre CA total ce mois-ci ?",
  "Quelles recettes devrais-je optimiser en priorité ?",
];

const SESSION_ID = uuidv4();

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await postJSON<{ session_id: string; reply: string; message_count: number }>("/chat/", {
        session_id: SESSION_ID,
        message: text,
      });
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Erreur de connexion à l'assistant." }]);
    } finally {
      setLoading(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      <h1 className="text-xl font-semibold text-gray-900 mb-4">Assistant IA — Données en temps réel</h1>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="space-y-3">
            <p className="text-sm text-gray-500">Posez une question sur vos données métier :</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-sm px-3 py-1.5 bg-white border border-gray-200 rounded-full hover:bg-brand-50 hover:border-brand-300 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                m.role === "user"
                  ? "bg-brand-600 text-white"
                  : "bg-white border border-gray-200 text-gray-900"
              }`}
            >
              {m.role === "assistant" ? (
                <ReactMarkdown className="prose prose-sm max-w-none">{m.content}</ReactMarkdown>
              ) : (
                m.content
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 text-sm text-gray-400">
              L'assistant analyse vos données…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); send(input); }}
        className="flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Posez votre question…"
          className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-brand-600 text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-brand-700 disabled:opacity-50 transition-colors"
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}
