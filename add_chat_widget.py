import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Check if chat widget already exists
if 'ChatWidget' in code or 'chat-messages' in code:
    print('Chat widget already exists')
    exit(0)

# 1. Add ChatWidget component before the main App function
chat_component = '''/* --- Chat Widget --- */
const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hello! I am SAFEGUARD AI assistant. Ask me about safety data, danger zones, risk levels, or what actions to take next.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMsg })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'bot', text: data.answer }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Sorry, I could not process that request. Please try again.' }]);
    }
    setLoading(false);
  };

  const quickQuestions = [
    'Which location is most hazardous?',
    'What are the danger zones?',
    'What should I do next?',
    'Give me a summary'
  ];

  return (
    <div style={{ position: 'fixed', bottom: 20, right: 20, zIndex: 9999, fontFamily: 'Inter, sans-serif' }}>
      {isOpen ? (
        <div style={{ width: 380, height: 500, background: '#0B1927', border: '1px solid #1C3446', borderRadius: 12, display: 'flex', flexDirection: 'column', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}>
          {/* Header */}
          <div style={{ padding: '14px 16px', background: '#0D1D2B', borderRadius: '12px 12px 0 0', borderBottom: '1px solid #1C3446', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 20 }}>🛡️</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#E7EDF3' }}>SAFEGUARD AI</div>
                <div style={{ fontSize: '0.7rem', color: '#22C55E' }}>● Online</div>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', color: '#91A3B7', fontSize: 20, cursor: 'pointer' }}>✕</button>
          </div>
          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: 12, display: 'flex', flexDirection: 'column', gap: 10 }}>
            {messages.map((msg, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{ maxWidth: '85%', padding: '10px 14px', borderRadius: msg.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px', fontSize: '0.82rem', lineHeight: 1.5, whiteSpace: 'pre-line', background: msg.role === 'user' ? '#18C6D9' : '#12263A', color: msg.role === 'user' ? '#000' : '#E7EDF3', border: msg.role === 'user' ? 'none' : '1px solid #1C3446' }}>
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{ padding: '10px 14px', borderRadius: '12px 12px 12px 2px', background: '#12263A', border: '1px solid #1C3446', color: '#91A3B7', fontSize: '0.82rem' }}>
                  Analyzing safety data...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          {/* Quick Questions */}
          {messages.length <= 1 && (
            <div style={{ padding: '8px 12px', display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {quickQuestions.map((q, i) => (
                <button key={i} onClick={() => { setInput(q); }} style={{ padding: '6px 10px', borderRadius: 16, border: '1px solid #1C3446', background: 'rgba(24,198,217,0.1)', color: '#18C6D9', fontSize: '0.7rem', cursor: 'pointer', fontWeight: 500 }}>
                  {q}
                </button>
              ))}
            </div>
          )}
          {/* Input */}
          <div style={{ padding: '10px 12px', borderTop: '1px solid #1C3446', display: 'flex', gap: 8 }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about safety data..."
              style={{ flex: 1, padding: '10px 12px', borderRadius: 8, border: '1px solid #1C3446', background: '#07111D', color: '#E7EDF3', fontSize: '0.82rem', outline: 'none' }}
            />
            <button onClick={sendMessage} disabled={!input.trim() || loading} style={{ padding: '10px 14px', borderRadius: 8, border: 'none', background: '#18C6D9', color: '#000', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}>
              Send
            </button>
          </div>
        </div>
      ) : (
        <button onClick={() => setIsOpen(true)} style={{ width: 60, height: 60, borderRadius: 30, border: '2px solid #18C6D9', background: '#0B1927', color: '#18C6D9', fontSize: 28, cursor: 'pointer', boxShadow: '0 4px 20px rgba(24,198,217,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          💬
        </button>
      )}
    </div>
  );
};

'''

# Insert before the MAIN APP comment
marker = '/* ══════════════════════════════════════════════════════════\n   MAIN APP\n   ══════════════════════════════════════════════════════════ */'
if marker not in code:
    # Try alternate marker
    marker = 'MAIN APP'
    m = re.search(r'/\*.*?MAIN APP.*?\*/', code, re.DOTALL)
    if m:
        code = code[:m.start()] + chat_component + code[m.start():]
    else:
        print('ERROR: Cannot find MAIN APP marker')
        exit(1)
else:
    code = code.replace(marker, chat_component + '\n' + marker)

# 2. Add ChatWidget to the render output (before closing </div> of app-container)
# Find the last closing div of app-container
render_marker = '  );\n}\n\nexport default App;'
if render_marker in code:
    code = code.replace(render_marker, '''      {/* Chat Widget */}
      <ChatWidget />
    </div>
  );
}

export default App;''')
    print('ChatWidget added to render')
else:
    print('WARNING: Could not find render end, trying alternate')
    # Try to find the export
    alt = 'export default App;'
    if alt in code:
        # Find the last </div> before export
        idx = code.rfind('</div>', 0, code.index(alt))
        if idx > 0:
            code = code[:idx] + '\n      {/* Chat Widget */}\n      <ChatWidget />\n    ' + code[idx:]

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

print('Chat widget added successfully')
