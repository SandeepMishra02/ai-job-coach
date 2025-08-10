// src/pages/InterviewPage.tsx
import { useState } from "react";
import { api } from "../api";

type Msg = { role: "you" | "coach"; text: string };

function readLog(): Msg[] {
  const raw = localStorage.getItem("coach_log");
  if (!raw) return [];
  try {
    const arr = JSON.parse(raw) as Array<{ role: string; text: string }>;
    // sanitize to our union type
    return arr
      .map((m) =>
        (m && (m.role === "you" || m.role === "coach") && typeof m.text === "string")
          ? ({ role: m.role, text: m.text } as Msg)
          : null
      )
      .filter(Boolean) as Msg[];
  } catch {
    return [];
  }
}

export default function InterviewPage() {
  const [input, setInput] = useState("");
  const [log, setLog] = useState<Msg[]>(() => readLog());
  const [loading, setLoading] = useState(false);

  function persist(next: Msg[]) {
    setLog(next);
    localStorage.setItem("coach_log", JSON.stringify(next));
  }

  async function send() {
    const q = input.trim();
    if (!q) return;
    setInput("");
    const next = [...log, { role: "you", text: q } as Msg];
    persist(next);

    setLoading(true);
    try {
      const { reply } = await api.interviewCoach(q);
      persist([...next, { role: "coach", text: reply } as Msg]);
    } catch (e) {
      console.error(e);
      persist([...next, { role: "coach", text: "Sorry, I hit an error." } as Msg]);
    } finally {
      setLoading(false);
    }
  }

  function clear() {
    if (!confirm("Clear conversation?")) return;
    persist([]);
  }

  return (
    <div className="stack">
      <section className="card">
        <header>Interview Coach</header>
        <div className="chat">
          {log.length === 0 && (
            <div className="chat-empty">
              Ask me anything — behavioral, system design, troubleshooting, or follow-ups.
            </div>
          )}
          {log.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              <div className="bubble-role">{m.role === "you" ? "You" : "Coach"}</div>
              <div className="bubble-text">{m.text}</div>
            </div>
          ))}
        </div>
        <div className="row">
          <input
            placeholder="Ask an interview question…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <button onClick={send} disabled={loading}>
            {loading ? "Thinking…" : "Send"}
          </button>
          <button className="ghost" onClick={clear}>
            Clear
          </button>
        </div>
      </section>
    </div>
  );
}

