"use client";

import { useState } from "react";

interface Message {
  role: "user" | "assistant";
  text: string;
  sources?: string[];
}

const GRAPHQL_URL = process.env.NEXT_PUBLIC_GRAPHQL_URL || "http://localhost:8000/graphql";

async function askQuestion(question: string): Promise<{ text: string; sources: string[] }> {
  const query = `
    query Ask($q: String!) {
      askQuestion(question: $q) { text sources }
    }
  `;
  const res = await fetch(GRAPHQL_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables: { q: question } }),
  });
  const json = await res.json();
  return json.data.askQuestion;
}

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Ask me about returns, shipping, or warranty." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const question = input;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const { text, sources } = await askQuestion(question);
      setMessages((m) => [...m, { role: "assistant", text, sources }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "assistant", text: "Sorry, something went wrong." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Support Assistant</h1>
      <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, minHeight: 300 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ margin: "12px 0", textAlign: m.role === "user" ? "right" : "left" }}>
            <div style={{
              display: "inline-block", padding: "8px 12px", borderRadius: 12,
              background: m.role === "user" ? "#dceeff" : "#f0f0f0", maxWidth: "80%",
            }}>
              {m.text}
              {m.sources && m.sources.length > 0 && (
                <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
                  Sources: {m.sources.join(", ")}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <p>Thinking…</p>}
      </div>
      <form onSubmit={handleSend} style={{ marginTop: 12 }}>
        <input
          style={{ width: "80%" }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. Can I return an opened laptop?"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
