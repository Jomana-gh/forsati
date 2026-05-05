import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./Chatbot.css";

const API = "https://forsati-api.onrender.com";

const suggestedQuestionsAr = [
  "وين أفضل حي لفتح مطعم في الرياض؟",
  "أي حي فيه أعلى كثافة سكانية؟",
  "وين أفتح صيدلية بأقل منافسة؟",
];

const suggestedQuestionsEn = [
  "What is the best neighborhood for a restaurant in Riyadh?",
  "Which neighborhoods have the least competition for shops?",
  "Which neighborhood has the highest population density?",
  "Where can I open a pharmacy with low competition?",
];

export default function Chatbot({ lang = "ar", t }) {
  const [open, setOpen] = useState(false);
  const welcomeMsg = lang === "ar"
    ? "مرحباً! أنا مساعد فرصتي\nاسألني عن أي حي في الرياض وسأساعدك تختار أفضل موقع لمشروعك."
    : "Hello! I am Forsati Assistant\nAsk me about any neighborhood in Riyadh and I will help you choose the best location for your business.";

  const [messages, setMessages] = useState([
    { role: "bot", text: welcomeMsg },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  const sendMessage = async (text) => {
    const question = (text || input).trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      // ✅ إرسال اللغة مع السؤال
      const res = await axios.post(`${API}/api/chat`, { 
        question: question,
        lang: lang
      });
      const { answer, sources } = res.data;

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: answer,
          sources: sources || [],
        },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: lang === "ar" ? "عذراً، حدث خطأ. تأكدي إن السيرفر شغال" : "Sorry, an error occurred. Please make sure the server is running.",
          error: true,
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <>
      <button className="chat-fab" onClick={() => setOpen((o) => !o)} aria-label="المساعد الذكي">
        {open ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="24" height="24">
            <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
            <path d="M20 2H4a2 2 0 00-2 2v18l4-4h14a2 2 0 002-2V4a2 2 0 00-2-2zm-2 10H6V10h12v2zm0-3H6V7h12v2z" />
          </svg>
        )}
      </button>

      {open && (
        <div className="chat-window" dir={lang === "ar" ? "rtl" : "ltr"}>
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="chat-avatar">✦</div>
              <div>
                <div className="chat-name">{lang === "ar" ? "مساعد فرصتي" : "Forsati Assistant"}</div>
                <div className="chat-status">● {lang === "ar" ? "مدعوم بالذكاء الاصطناعي" : "AI Powered"}</div>
              </div>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)}>✕</button>
          </div>

          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble-wrap ${msg.role}`}>
                {msg.role === "bot" && <div className="bubble-avatar">✦</div>}
                <div className={`chat-bubble ${msg.role} ${msg.error ? "error" : ""}`}>
                  <p style={{ whiteSpace: "pre-line", margin: 0 }}>{msg.text}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="chat-sources">
                      <span className="sources-label">{lang === "ar" ? "📍 الأحياء المستخدمة:" : "📍 Neighborhoods referenced:"}</span>
                      <div className="sources-tags">
                        {msg.sources.map((s, j) => (
                          <span key={j} className="source-tag">{s}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="chat-bubble-wrap bot">
                <div className="bubble-avatar">✦</div>
                <div className="chat-bubble bot loading-bubble">
                  <span className="dot" /><span className="dot" /><span className="dot" />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {messages.length === 1 && (
            <div className="chat-suggestions">
              {(lang === "ar" ? suggestedQuestionsAr : suggestedQuestionsEn).map((q, i) => (
                <button key={i} className="suggestion-btn" onClick={() => sendMessage(q)}>
                  {q}
                </button>
              ))}
            </div>
          )}

          <div className="chat-input-area">
            <input
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder={lang === "ar" ? "اسأل عن أي حي في الرياض..." : "Ask about any neighborhood in Riyadh..."}
              disabled={loading}
            />
            <button
              className="chat-send"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
}