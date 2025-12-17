import React, { useState, useEffect } from 'react';
import { useLocation } from '@docusaurus/router';

// --- 1. Chatbot Component ---
function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{ text: "Hello! Main AI Tutor hun.", sender: "bot" }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setMessages([...messages, { text: userMsg, sender: "user" }]);
    setInput(""); setLoading(true);
    try {
      const res = await fetch("https://physical-ai-hackathon.onrender.com", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMsg }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { text: data.answer, sender: "bot" }]);
    } catch (e) { setMessages(prev => [...prev, { text: "Backend Error!", sender: "bot" }]); }
    setLoading(false);
  };

  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 9999 }}>
      {isOpen && (
        <div style={{ width: '300px', height: '400px', background: 'white', border: '1px solid #ddd', borderRadius: '10px', display: 'flex', flexDirection: 'column', marginBottom: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
          <div style={{ background: '#25c2a0', color: 'white', padding: '10px', borderRadius: '10px 10px 0 0' }}>🤖 AI Chat <button onClick={() => setIsOpen(false)} style={{ float: 'right', background: 'none', border: 'none', color: 'white' }}>✖</button></div>
          <div style={{ flex: 1, padding: '10px', overflowY: 'auto', background: '#f9f9f9' }}>
            {messages.map((m, i) => <div key={i} style={{ textAlign: m.sender === 'user' ? 'right' : 'left', margin: '5px 0' }}><span style={{ background: m.sender === 'user' ? '#007bff' : '#eee', color: m.sender === 'user' ? 'white' : 'black', padding: '5px 10px', borderRadius: '10px', display: 'inline-block' }}>{m.text}</span></div>)}
            {loading && <div>...</div>}
          </div>
          <div style={{ padding: '10px', display: 'flex' }}><input value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && sendMessage()} style={{ flex: 1 }} placeholder="Ask..." /><button onClick={sendMessage}>Send</button></div>
        </div>
      )}
      <button onClick={() => setIsOpen(!isOpen)} style={{ width: '50px', height: '50px', borderRadius: '50%', background: '#25c2a0', color: 'white', border: 'none', fontSize: '24px', cursor: 'pointer' }}>💬</button>
    </div>
  );
}

// --- 2. Personalization & Translation Manager ---
function ContentManager() {
  const [loading, setLoading] = useState(false);
  const [hardware, setHardware] = useState(localStorage.getItem('user_hardware') || 'cpu');

  // Hardware Save Karna
  const handleHardwareChange = (e) => {
    const val = e.target.value;
    setHardware(val);
    localStorage.setItem('user_hardware', val);
    alert(`Settings Saved: Optimized for ${val === 'gpu' ? 'NVIDIA RTX GPU' : 'Standard CPU'}`);
  };

  // Generic Function: Content ko Server bhejna aur update karna
  const processContent = async (endpoint, payloadExtra = {}) => {
    const article = document.querySelector('article');
    if (!article) return alert("Content nahi mila!");
    
    setLoading(true);
    const originalText = article.innerText.substring(0, 3000); // Limit for demo

    try {
      const res = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: originalText, ...payloadExtra }),
      });
      const data = await res.json();
      const newText = data.translated_text || data.personalized_text;

      if (newText) {
        article.innerHTML = `
          <div style="border: 2px dashed #25c2a0; padding: 20px; border-radius: 10px; background: #f0fdfa;">
            <h2 style="color: #25c2a0;">✨ AI Content Updated</h2>
            <p><strong>Mode:</strong> ${endpoint === '/translate' ? 'Urdu Translation' : 'Personalized (' + hardware.toUpperCase() + ')'}</p>
            <hr/>
            <div style="${endpoint === '/translate' ? 'direction: rtl; font-family: Noto Nastaliq Urdu; font-size: 1.2em;' : ''}">
              ${newText.replace(/\n/g, '<br/>')}
            </div>
          </div>
        `;
      }
    } catch (e) { alert("Failed. Backend check karein."); }
    setLoading(false);
  };

  return (
    <div style={{ position: 'fixed', top: '70px', right: '20px', zIndex: 9998, display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'flex-end' }}>
      
      {/* Hardware Selector Dropdown */}
      <select 
        value={hardware} 
        onChange={handleHardwareChange}
        style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ccc', cursor: 'pointer' }}
      >
        <option value="cpu">💻 I have CPU (Standard)</option>
        <option value="gpu">🚀 I have NVIDIA GPU (RTX)</option>
      </select>

      {/* Buttons */}
      <div style={{ display: 'flex', gap: '5px' }}>
        <button 
          onClick={() => processContent('/personalize', { hardware })}
          disabled={loading}
          style={{ padding: '8px 15px', background: '#4ec9b0', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          {loading ? "Processing..." : "⚡ Personalize"}
        </button>

        <button 
          onClick={() => processContent('/translate')}
          disabled={loading}
          style={{ padding: '8px 15px', background: '#ff6b6b', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          🇮🇹 Urdu
        </button>
      </div>
    </div>
  );
}

// --- Main Export ---
export default function Root({children}) {
  const location = useLocation();
  const isDocsPage = location.pathname.startsWith('/docs');

  return (
    <>
      {children}
      <Chatbot />
      {isDocsPage && <ContentManager />}
    </>
  );
}