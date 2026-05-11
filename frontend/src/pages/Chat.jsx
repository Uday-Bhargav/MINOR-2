import { Send } from "lucide-react";
import { useState } from "react";

import { api } from "../api.js";

export default function Chat() {
  const [message, setMessage] = useState("What happened to oil stocks last week?");
  const [thread, setThread] = useState([]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed) return;
    setThread((items) => [...items, { role: "user", text: trimmed }]);
    setMessage("");
    setLoading(true);
    try {
      const response = await api.chat(trimmed);
      setThread((items) => [...items, { role: "assistant", text: response.answer }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-page">
      <header className="page-header">
        <div>
          <span className="eyebrow">AI market analyst</span>
          <h1>Ask about crisis impact</h1>
          <p>The chatbot uses stored events and predictions as context.</p>
        </div>
      </header>

      <section className="chat-window" aria-live="polite">
        {thread.length === 0 ? <div className="empty-state">Ask a question about sectors, events, or recent crisis signals.</div> : null}
        {thread.map((item, index) => (
          <div key={`${item.role}-${index}`} className={`message ${item.role}`}>
            {item.text}
          </div>
        ))}
        {loading ? <div className="message assistant">Thinking through stored signals...</div> : null}
      </section>

      <form className="chat-input" onSubmit={onSubmit}>
        <input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask about oil, airlines, banks..." />
        <button className="primary-button" type="submit" aria-label="Send message">
          <Send size={18} aria-hidden="true" />
        </button>
      </form>
    </div>
  );
}

