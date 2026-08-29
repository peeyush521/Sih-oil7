import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from "chart.js";
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Auth from './Auth';
import { supabase } from './supabase';
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import CytoscapeComponent from 'react-cytoscapejs';

/* ── Typewriter ─────────────────────────────────────────── */
const Typewriter = ({ text }) => {
  const [content, setContent] = useState('');
  useEffect(() => {
    setContent('');
    let i = 0;
    const cleanText = text.replace(/\*\*(.*?)\*\*/g, '$1');
    const timer = setInterval(() => {
      setContent(cleanText.slice(0, i));
      i++;
      if (i > cleanText.length) clearInterval(timer);
    }, 15);
    return () => clearInterval(timer);
  }, [text]);
  return <div style={{ fontSize: '0.8rem', lineHeight: '1.6', fontFamily: 'var(--font-mono)' }}>{content}<span style={{ animation: 'blink 1s step-end infinite', opacity: 0.5 }}>|</span></div>;
};

/* ── Alarm Sound Generator ─────────────────────────────── */
const useAlarmSound = () => {
  const playAlarm = useCallback(() => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      // Three-tone siren
      [880, 660, 880].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = 'square';
        osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.15);
        gain.gain.setValueAtTime(0.06, ctx.currentTime + i * 0.15);
        gain.gain.linearRampToValueAtTime(0, ctx.currentTime + i * 0.15 + 0.15);
        osc.start(ctx.currentTime + i * 0.15);
        osc.stop(ctx.currentTime + i * 0.15 + 0.15);
      });
    } catch (e) {}
  }, []);
  return playAlarm;
};

/* ── Alert Banner ──────────────────────────────────────── */
const AlertBanner = ({ report, risk, onDismiss }) => (
  <div className="alert-banner" onClick={onDismiss} style={{ cursor: 'pointer' }}>
    <div className="alert-icon">🚨</div>
    <div className="alert-content" style={{ flex: 1 }}>
      <h3>PRECURSOR DETECTED — {report?.id}</h3>
      <p style={{ fontSize: '0.85rem', marginTop: 4 }}>
        Risk Score: <strong style={{ color: 'var(--critical)' }}>{risk?.score}/100</strong> — 
        SIF Pathway: <strong style={{ color: 'var(--warning)' }}>{risk?.sif_category}</strong> — 
        Trajectory: <strong>{risk?.trajectory}</strong>
      </p>
    </div>
    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Click to dismiss</div>
  </div>
);

/* ── Bar Chart Component ───────────────────────────────── */
const BarChart = ({ data, title, color = 'var(--primary)' }) => {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  const maxVal = Math.max(...entries.map(e => e[1]), 1);
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: 10 }}>{title}</div>
      {entries.map(([key, val], idx) => (
        <div key={key} style={{ display: 'flex', alignItems: 'center', marginBottom: 6, gap: 8 }}>
          <div style={{ width: 110, fontSize: '0.72rem', color: 'var(--text-muted)', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: idx < 3 ? 700 : 400 }}>{idx < 3 ? '🔴 ' : ''}{key.replace(/_/g, ' ')}</div>
          <div style={{ flex: 1, height: 18, background: 'var(--bg-surface2)', borderRadius: 4, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${(val / maxVal) * 100}%`, background: color, borderRadius: 4, transition: 'width 0.5s ease', display: 'flex', alignItems: 'center', paddingLeft: 6 }}>
              <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#fff' }}>{val}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

/* ── Risk Sparkline ────────────────────────────────────── */
const RiskSparkline = ({ data }) => {
  if (!data || data.length === 0) return null;
  const max = 100;
  const h = 60;
  const w = 300;
  const points = data.map((d, i) => {
    const x = (i / Math.max(data.length - 1, 1)) * w;
    const y = h - (d.score / max) * h;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={w} height={h} style={{ display: 'block' }}>
      <defs>
        <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--critical)" stopOpacity="0.3" />
          <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={`0,${h} ${points} ${w},${h}`} fill="url(#sparkGrad)" />
      <polyline points={points} fill="none" stroke="var(--primary)" strokeWidth="2" />
      {data.map((d, i) => {
        const x = (i / Math.max(data.length - 1, 1)) * w;
        const y = h - (d.score / max) * h;
        return <circle key={i} cx={x} cy={y} r={d.is_precursor ? 5 : 3} fill={d.is_precursor ? 'var(--critical)' : 'var(--primary)'} />;
      })}
    </svg>
  );
};

/* --- Chat Widget --- */
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


/* ══════════════════════════════════════════════════════════
   MAIN APP
   ══════════════════════════════════════════════════════════ */


const LocationMap = ({ analytics }) => {
  if (!analytics) return null;
  
  // Duliajan Oil India facility coordinates (approximate)
  const locations = {
    'UNIT_A': { lat: 27.1500, lng: 94.7200, name: 'Unit A - Processing' },
    'UNIT_B': { lat: 27.1510, lng: 94.7210, name: 'Unit B - Storage' },
    'UNIT_C': { lat: 27.1520, lng: 94.7220, name: 'Unit C - Drilling' },
    'WAREHOUSE_C': { lat: 27.1490, lng: 94.7190, name: 'Warehouse C' },
    'LOCAL_01': { lat: 27.1530, lng: 94.7230, name: 'Admin Block' },
    'LOCAL_02': { lat: 27.1540, lng: 94.7240, name: 'Maintenance Shop' },
    'LOCAL_03': { lat: 27.1550, lng: 94.7250, name: 'Pump House' },
    'LOCAL_04': { lat: 27.1560, lng: 94.7260, name: 'Control Room' },
    'LOCAL_05': { lat: 27.1570, lng: 94.7270, name: 'Tank Farm' },
    'Unit_A_Processing': { lat: 27.1500, lng: 94.7200, name: 'Unit A - Processing' },
    'Unit_B_Production': { lat: 27.1510, lng: 94.7210, name: 'Unit B - Production' },
    'Unit_C_Treatment': { lat: 27.1520, lng: 94.7220, name: 'Unit C - Treatment' },
    'Pump_House_PH01': { lat: 27.1550, lng: 94.7250, name: 'Pump House PH-01' },
    'Tank_Farm_TF01': { lat: 27.1570, lng: 94.7270, name: 'Tank Farm TF-01' },
    'Warehouse_WH01': { lat: 27.1490, lng: 94.7190, name: 'Warehouse WH-01' },
    'Warehouse_WH02': { lat: 27.1495, lng: 94.7195, name: 'Warehouse WH-02' },
    'Maintenance_Shop_MS01': { lat: 27.1540, lng: 94.7240, name: 'Maintenance Shop' },
    'Control_Room_CR01': { lat: 27.1560, lng: 94.7260, name: 'Control Room' },
    'Admin_Building_AB01': { lat: 27.1530, lng: 94.7230, name: 'Admin Building' },
    'Chemical_Storage_CS01': { lat: 27.1580, lng: 94.7280, name: 'Chemical Storage' },
    'Well_Pad_WP01': { lat: 27.1450, lng: 94.7150, name: 'Well Pad WP-01' },
    'Well_Pad_WP02': { lat: 27.1460, lng: 94.7160, name: 'Well Pad WP-02' },
    'Well_Pad_WP03': { lat: 27.1470, lng: 94.7170, name: 'Well Pad WP-03' },
    'Pipe_Rack_PR01': { lat: 27.1515, lng: 94.7215, name: 'Pipe Rack PR-01' },
    'Pipe_Rack_PR02': { lat: 27.1525, lng: 94.7225, name: 'Pipe Rack PR-02' },
    'Loading_Bay_LB01': { lat: 27.1485, lng: 94.7185, name: 'Loading Bay' },
    'Laydown_Area_LA01': { lat: 27.1480, lng: 94.7180, name: 'Laydown Area' },
    'Substation_SS01': { lat: 27.1505, lng: 94.7205, name: 'Substation' },
    'Workshop_WS01': { lat: 27.1535, lng: 94.7235, name: 'Workshop' },
    'Laboratory_LAB01': { lat: 27.1545, lng: 94.7245, name: 'Laboratory' },
    'Effluent_Treatment_ET01': { lat: 27.1600, lng: 94.7300, name: 'Effluent Treatment' },
    'Gas_Processing_GP01': { lat: 27.1440, lng: 94.7140, name: 'Gas Processing' },
    'Flare_Pit_FP01': { lat: 27.1430, lng: 94.7130, name: 'Flare Pit' },
    'Fuel_Farm_FF01': { lat: 27.1575, lng: 94.7275, name: 'Fuel Farm' },
    'Tool_Room_TR01': { lat: 27.1542, lng: 94.7242, name: 'Tool Room' },
    'Scaffold_Tower_T3': { lat: 27.1518, lng: 94.7218, name: 'Scaffold Tower T3' },
    'Elevated_Platform_EP01': { lat: 27.1528, lng: 94.7228, name: 'Elevated Platform' },
  };
  
  const dist = analytics.location_distribution || {};
  
  return (
    <div style={{ height: '350px', borderRadius: 8, overflow: 'hidden', border: '1px solid var(--border)' }}>
      <MapContainer center={[27.153, 94.723]} zoom={15} style={{ height: '100%', width: '100%' }} scrollWheelZoom={false}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {Object.entries(locations).map(([key, loc]) => {
          const count = dist[key] || 0;
          if (count === 0) return null;
          const radius = Math.min(5 + count * 3, 20);
          const color = count >= 4 ? '#ef4444' : count >= 2 ? '#f59e0b' : '#10b981';
          return (
            <CircleMarker key={key} center={[loc.lat, loc.lng]} radius={radius} fillColor={color} fillOpacity={0.7} color={color} weight={2}>
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif' }}>
                  <strong>{loc.name}</strong><br/>
                  Incidents: <strong>{count}</strong><br/>
                  Risk: {count >= 4 ? 'HIGH' : count >= 2 ? 'MEDIUM' : 'LOW'}
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
};

const RiskChart = ({ reports }) => {
  if (!reports || !Array.isArray(reports) || reports.length === 0) return <div className="empty-state">No timeline data</div>;
  
  const labels = reports.map((r, i) => 'D' + (i + 1));
  const scores = reports.map(r => r.risk_data.score);
  const colors = reports.map(r => r.is_precursor ? '#ef4444' : '#18c6d9');
  
  const data = {
    labels,
    datasets: [{
      label: 'Risk Score',
      data: scores,
      borderColor: '#18c6d9',
      backgroundColor: 'rgba(24, 198, 217, 0.1)',
      fill: true,
      tension: 0.3,
      pointBackgroundColor: colors,
      pointRadius: 6,
      pointHoverRadius: 8,
    }]
  };
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          afterLabel: (ctx) => {
            const r = reports[ctx.dataIndex];
            return r.is_precursor ? 'PRECURSOR DETECTED' : '';
          }
        }
      }
    },
    scales: {
      y: {
        min: 0, max: 100,
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: '#94a3b8' }
      },
      x: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: '#94a3b8' }
      }
    }
  };
  
  return (
    <div style={{ position: 'relative', height: '200px' }}>
      <Line data={data} options={options} />
      <div style={{ position: 'absolute', top: '30%', right: 10, background: 'rgba(239,68,68,0.2)', border: '1px solid #ef4444', padding: '2px 8px', borderRadius: 4, fontSize: '0.7rem', color: '#ef4444' }}>
        CRITICAL THRESHOLD (70)
      </div>
    </div>
  );
};

function App() {
  const [stateData, setStateData] = useState(null);
  const [currentState, setCurrentState] = useState(null);
  const [graphElements, setGraphElements] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [simResults, setSimResults] = useState("Select an intervention to see predicted risk trajectory.");
  const [cy, setCy] = useState(null);
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [customText, setCustomText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [alertDismissed, setAlertDismissed] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [alarmActive, setAlarmActive] = useState(false);
  const [showMobileInput, setShowMobileInput] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  const playAlarm = useAlarmSound();

  // Check Supabase session on mount
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setAuthLoading(false);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });
    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  // Alarm: play sound + flash when precursor detected
  useEffect(() => {
    if (currentState?.is_precursor) {
      setAlarmActive(true);
      playAlarm();
      setAlertDismissed(false);
      const interval = setInterval(playAlarm, 2500);
      return () => {
        clearInterval(interval);
        setAlarmActive(false);
      };
    } else {
      setAlarmActive(false);
    }
  }, [currentState?.is_precursor, playAlarm]);

  const handleNavClick = (e, tabName, targetId) => {
    e.preventDefault();
    setActiveTab(tabName);
    if (targetId) {
      const el = document.getElementById(targetId);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const loadState = async () => {
    try {
      const res = await fetch('/api/state');
      const data = await res.json();
      setStateData(data);
      if (data.reports.length > 0) {
        setCurrentState(data.reports[data.reports.length - 1]);
        fetchGraph();
      } else {
        setCurrentState(null);
        setGraphElements([]);
      }
    } catch (e) { console.error(e); }
  };

  const loadAnalytics = async () => {
    try {
      const res = await fetch('/api/analytics');
      const data = await res.json();
      setAnalytics(data);
    } catch (e) { console.error(e); }
  };

  const fetchGraph = async () => {
    try {
      const res = await fetch('/api/graph_data');
      const data = await res.json();
      setGraphElements(data);
      if (cy) cy.layout({ name: 'cose', animate: true, padding: 30 }).run();
    } catch (e) { console.error(e); }
  };

  useEffect(() => { loadState(); loadAnalytics(); }, []);

  const processNext = async () => {
    setProcessing(true);
    try {
      const res = await fetch('/api/process_next', { method: 'POST' });
      if (!res.ok) { if (res.status === 400) alert("All reports processed — simulation complete"); return; }
      const data = await res.json();
      setCurrentState(data);
      await loadState();
      await loadAnalytics();
      setSimResults("Select an intervention to see predicted risk trajectory.");
    } catch (e) { console.error(e); }
    finally { setProcessing(false); }
  };

  const submitCustomReport = async () => {
    if (!customText.trim()) return;
    setSubmitting(true);
    try {
      const res = await fetch('/api/submit_report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: customText.trim() })
      });
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      setCurrentState(data);
      setCustomText('');
      await loadState();
      await loadAnalytics();
      setSimResults("Select an intervention to see predicted risk trajectory.");
    } catch (e) { alert('Failed to analyze report'); }
    finally { setSubmitting(false); }
  };

  const resetSimulation = async () => {
    await fetch('/api/reset');
    setAlarmActive(false);
    await loadState();
    setAnalytics(null);
    setSimResults("Select an intervention to see predicted risk trajectory.");
  };

  const simulateIntervention = async (action) => {
    if (!currentState) return;
    try {
      const res = await fetch(`/api/simulate?intervention_type=${action}`, { method: 'POST' });
      const data = await res.json();
      setSimResults(
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <span style={{ fontSize: '2rem', fontWeight: 'bold' }}>{data.risk_score}</span>
          <span className={`risk-trend ${data.trajectory.toLowerCase()}`} style={{ marginLeft: 10 }}>
            {data.trajectory === 'ESCALATING' ? '↗' : (data.trajectory === 'DECREASING' ? '↘' : '→')} {data.trajectory}
          </span>
        </div>
      );
    } catch (e) { console.error(e); }
  };

  let precursors = 0, unresolved = 0;
  if (stateData && stateData.reports) {
    (stateData && stateData.reports ? stateData.reports : []).forEach(r => {
      if (r.is_precursor) precursors++;
      if (r.report && r.report.action_status === "Open") unresolved++;
    });
  }

  // Auth guard
  if (authLoading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-main)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16, animation: 'pulsing 2s infinite' }}>🛡️</div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Loading SAFEGUARD AI...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Auth onAuth={(u) => setUser(u)} />;
  }

  return (
    <div className="app-container">
      {/* ── Sidebar ─────────────────────────────────────── */}
      <div className="sidebar">
        <div className="logo" style={{ marginBottom: '10px' }}>
          <div className="logo-icon">🛡️</div>
          <h1>SAFEGUARD AI</h1>
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', letterSpacing: '0.5px', marginBottom: '40px', paddingLeft: '36px', fontWeight: '500' }}>
          Industrial Safety Intelligence
        </div>

        <div className="nav-menu">
          <a href="#" className={`nav-item ${activeTab === 'Dashboard' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Dashboard', null)}>◇ Dashboard</a>
          <a href="#" className={`nav-item ${activeTab === 'Reports' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Reports', 'incident-timeline')}>▤ Reports</a>
          <a href="#" className={`nav-item ${activeTab === 'Analytics' ? 'active' : ''}`} onClick={(e) => { handleNavClick(e, 'Analytics', 'analytics-panel'); loadAnalytics(); }}>📊 Analytics</a>
          <a href="#" className={`nav-item ${activeTab === 'Event Graph' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Event Graph', 'precursor-chain-panel')}>◇ Event Graph</a>
        </div>

        {/* User Info */}
        <div style={{ marginTop: 'auto', paddingTop: 12, borderTop: '1px solid var(--border)', marginBottom: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <div style={{ width: 32, height: 32, borderRadius: 16, background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 700, color: '#000' }}>
              {user.email?.charAt(0).toUpperCase() || '?'}
            </div>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user.email}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Signed in</div>
            </div>
          </div>
          <button onClick={handleLogout} className="btn secondary" style={{ width: '100%', padding: '6px', fontSize: '0.7rem', border: '1px solid rgba(239,68,68,0.3)', color: 'var(--critical)' }}>
            Sign Out
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button className="btn primary" onClick={processNext} disabled={processing} style={{ padding: '12px', fontSize: '0.95rem', fontWeight: 600 }}>
            {processing ? 'Analyzing...' : '＋ Load next report'}
          </button>
          <button className="btn secondary" onClick={resetSimulation} style={{ padding: '8px', fontSize: '0.8rem', border: 'none' }}>
            Reset timeline
          </button>
          <div style={{ display: 'flex', gap: 6 }}>
            <a href="/api/export" target="_blank" className="btn secondary" style={{ flex: 1, padding: '8px', fontSize: '0.75rem', textAlign: 'center', textDecoration: 'none', color: 'var(--text-main)' }}>
              📋 JSON
            </a>
            <a href="/api/export/pdf" target="_blank" className="btn secondary" style={{ flex: 1, padding: '8px', fontSize: '0.75rem', textAlign: 'center', textDecoration: 'none', color: 'var(--text-main)' }}>
              📄 PDF
            </a>
          </div>

          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '0.5px', fontWeight: 600, marginBottom: '8px' }}>CUSTOM INPUT</div>
            <textarea
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              placeholder='Type a safety report...'
              rows={4}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)', color: 'var(--text-main)', fontFamily: 'inherit', fontSize: '0.8rem', resize: 'vertical', marginBottom: '8px' }}
            />
            <button className="btn primary" onClick={submitCustomReport} disabled={submitting || !customText.trim()} style={{ padding: '10px', fontSize: '0.85rem' }}>
              {submitting ? 'Analyzing...' : '🔍 Analyze Custom Report'}
            </button>
          </div>
        </div>
      </div>

      {/* ── Main Content ────────────────────────────────── */}
      <div className={`main-content ${alarmActive ? 'critical-alarm-active' : ''}`}>

        {/* Alert Banner */}
        {alarmActive && !alertDismissed && currentState && (
          <AlertBanner report={currentState.report} risk={currentState.risk_data} onDismiss={() => setAlertDismissed(true)} />
        )}

        <div className="topbar">
          <h2>Command Center</h2>
          <div style={{ display: 'flex', gap: 16 }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', border: `1px solid ${alarmActive ? 'var(--critical)' : 'var(--border)'}`, padding: '6px 10px', borderRadius: '4px', background: alarmActive ? 'rgba(239,68,68,0.1)' : 'transparent' }}>
              <div style={{ color: alarmActive ? 'var(--critical)' : 'var(--primary)', fontSize: '0.6rem', marginTop: '2px' }}>●</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: '1.2' }}>{alarmActive ? '⚠ ALERT' : 'Simulation'}<br/>Mode</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', border: '1px solid var(--border)', padding: '6px 10px', borderRadius: '4px' }}>
              <div style={{ color: 'var(--safe)', fontSize: '0.6rem', marginTop: '2px' }}>●</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: '1.2' }}>AI Engine<br/>Online</div>
            </div>
          </div>
        </div>

        {/* ═══ DASHBOARD TAB ═══ */}
        {activeTab === 'Dashboard' && (
          <div className="dashboard-grid">

            {/* Risk Hero */}
            <div className="panel surface-panel col-span-2">
              <div className="panel-header">
                <h3>Safety Risk</h3>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600 }}>Active Precursor Status</div>
              </div>
              <div className="panel-body" style={{ display: 'flex', gap: 20 }}>
                {currentState ? (
                  <>
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                      <div className={`risk-circle ${currentState.is_precursor ? 'critical' : (currentState.risk_data.score >= 40 ? 'warning' : 'safe')}`}>
                        {currentState.risk_data.score}
                      </div>
                      <div className={`risk-status-text ${currentState.is_precursor ? 'critical' : (currentState.risk_data.score >= 40 ? 'warning' : 'safe')}`}>
                        {currentState.is_precursor ? 'CRITICAL' : (currentState.risk_data.score >= 40 ? 'WARNING' : 'NORMAL')}
                      </div>
                      <div className={`risk-trend ${currentState.risk_data.trajectory.toLowerCase()}`} style={{ textTransform: 'capitalize' }}>
                        {currentState.risk_data.trajectory.toLowerCase()}
                      </div>
                      {/* Sparkline */}
                      {stateData && stateData.reports.length > 1 && (
                        <div style={{ marginTop: 12, width: '100%' }}>
                          <RiskSparkline data={stateData && stateData.reports ? stateData.reports : []} />
                        </div>
                      )}
                    </div>
                    <div style={{ flex: 1.5, borderLeft: '1px solid var(--border)', paddingLeft: 30, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                      {currentState.is_precursor && (
                        <div style={{ marginBottom: 16 }}>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>SIF Pathway Detected</div>
                          <div style={{ display: 'inline-block', padding: '6px 12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--critical)', borderRadius: '4px', color: 'var(--critical)', fontWeight: 'bold' }}>
                            {currentState.risk_data.sif_category}
                          </div>
                        </div>
                      )}
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>Primary Target</div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--text-main)' }}>
                          {currentState.extracted_entities.equipment[0] || 'Unspecified Location'}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>Recommended Action</div>
                        <ul style={{ paddingLeft: 20, color: 'var(--text-main)', fontWeight: 500 }}>
                          {currentState.risk_data.evidence.length > 0 ? (
                            <li>Verify {currentState.extracted_entities.equipment[0] || 'area'} safety protocol</li>
                          ) : <li style={{ color: 'var(--text-muted)' }}>Monitor for further changes</li>}
                          <li>Close unresolved corrective actions</li>
                        </ul>
                      </div>
                    </div>
                  </>
                ) : <div className="empty-state">Waiting for report ingestion...</div>}
              </div>
            </div>

            {/* System Intelligence */}
            <div className="panel surface-panel">
              <div className="panel-header"><h3>System Intelligence</h3></div>
              <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {[['Last updated', new Date().toLocaleTimeString()], ['Signal confidence', '94%'], ['Reports analyzed', stateData ? stateData.total_reports : 0]].map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{k}</span>
                    <span style={{ fontWeight: 'bold', fontSize: '0.95rem', fontFamily: 'var(--font-mono)' }}>{v}</span>
                  </div>
                ))}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Active precursors</span>
                  <span style={{ fontWeight: 'bold', fontSize: '1.05rem', color: precursors > 0 ? 'var(--critical)' : 'var(--safe)' }}>{precursors}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Open actions</span>
                  <span style={{ fontWeight: 'bold', fontSize: '1.05rem', color: unresolved > 0 ? 'var(--warning)' : 'inherit' }}>{unresolved}</span>
                </div>
                <div style={{ marginTop: 'auto', paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn secondary" style={{ flex: 1, padding: '10px', fontSize: '0.85rem' }} onClick={() => simulateIntervention('delay')} disabled={!currentState}>Delay action</button>
                    <button className="btn safe" style={{ flex: 1, padding: '10px', fontSize: '0.85rem' }} onClick={() => simulateIntervention('resolve_action')} disabled={!currentState}>✓ Mark complete</button>
                  </div>
                  {simResults !== "Select an intervention to see predicted risk trajectory." && (
                    <div style={{ marginTop: 12, textAlign: 'center', background: 'var(--bg-surface2)', padding: '8px', borderRadius: '4px' }}>{simResults}</div>
                  )}
                </div>
              </div>
            </div>

            {/* Latest Signal */}
            <div className="panel surface-panel col-span-2">
              <div className="panel-header"><h3>Latest Processed Signal</h3></div>
              <div className="panel-body">
                {currentState ? (
                  <>
                    <div style={{ marginBottom: 8, fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-main)' }}>
                      {currentState.extracted_entities.hazards[0] ? `${currentState.extracted_entities.hazards[0].replace('_', ' ')} reported near ${currentState.extracted_entities.equipment[0] || 'area'}` : 'Routine safety report processed'}
                    </div>
                    <div style={{ marginBottom: 16, fontSize: '0.9rem', color: 'var(--text-muted)' }}>"{currentState.report.text}"</div>
                    <div>
                      <span className="tag incident">{currentState.report_class}</span>
                      {currentState.extracted_entities.equipment.map(e => <span key={e} className="tag equipment">{e}</span>)}
                      {currentState.extracted_entities.hazards.map(e => <span key={e} className="tag hazard">{e.replace('_', ' ')}</span>)}
                      {currentState.extracted_entities.locations.map(e => <span key={e} className="tag location">{e}</span>)}
                    </div>
                  </>
                ) : <div className="empty-state">Waiting for next report...</div>}
              </div>
            </div>

            {/* AI Reasoning */}
            <div className="panel surface-panel">
              <div className="panel-header"><h3>AI Reasoning</h3></div>
              <div className="panel-body" style={{ background: 'rgba(24, 198, 217, 0.02)', borderLeft: '3px solid var(--primary)', overflowY: 'auto' }}>
                {currentState ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', height: '100%' }}>
                    <div style={{ color: 'var(--text-main)', fontWeight: 600, fontSize: '0.9rem' }}>
                      Why is {currentState.extracted_entities.equipment[0] || 'this event'} considered high risk?
                    </div>
                    <div style={{ flex: 1, fontFamily: 'var(--font-mono)' }}>
                      <Typewriter text={currentState.llm_explanation} />
                    </div>
                    <div style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', color: 'var(--text-muted)', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                      <div>Confidence: <span style={{ color: 'var(--safe)', fontWeight: 'bold' }}>94%</span></div>
                      <div>{currentState.extracted_entities.hazards.length} related events</div>
                    </div>
                  </div>
                ) : <div className="empty-state">Waiting for AI...</div>}
              </div>
            </div>

            {/* Risk Trajectory */}
            <div className="panel surface-panel col-span-2">
              <div className="panel-header"><h3>Risk Trajectory</h3></div>
              <div className="panel-body">
                <RiskChart reports={stateData && stateData.reports ? stateData.reports : []} />
              </div>
            </div>

            {/* Why Now */}
            <div className="panel surface-panel">
              <div className="panel-header"><h3>Why Now?</h3></div>
              <div className="panel-body">
                {currentState && currentState.risk_data.deltas && Object.keys(currentState.risk_data.deltas).length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                    {Object.entries(currentState.risk_data.deltas).map(([factor, score]) => (
                      <div key={factor} className="evidence-bar-container">
                        <div className="evidence-bar-header"><span>{factor}</span><span className="val">+{score}</span></div>
                        <div className="evidence-bar-bg"><div className="evidence-bar-fill" style={{ width: `${Math.min((score / 20) * 100, 100)}%` }}></div></div>
                      </div>
                    ))}
                    <div style={{ marginTop: 'auto', paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600 }}>Evidence Source</div>
                      <div className="node-details">
                        <div style={{ color: 'var(--primary)', fontWeight: 'bold', marginBottom: 4 }}>Report #{currentState.report.id.substring(0, 8)}</div>
                        <div style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>"{currentState.report.text}"</div>
                      </div>
                    </div>
                  </div>
                ) : <div className="empty-state">No significant risk multipliers active.</div>}
              </div>
            </div>

            {/* Graph */}
            <div className="panel surface-panel col-span-2" id="precursor-chain-panel" style={{ height: 400 }}>
              <div className="panel-header"><h3>Precursor Chain (Temporal Graph)</h3></div>
              <div className="panel-body" style={{ padding: 0 }}>
                <CytoscapeComponent
                  elements={graphElements}
                  style={{ width: '100%', height: '100%' }}
                  stylesheet={[
                    { selector: 'node', style: { 'background-color': '#3b82f6', 'label': 'data(label)', 'color': '#fff', 'text-valign': 'center', 'text-outline-width': 2, 'text-outline-color': '#0f172a', 'font-size': '10px' } },
                    { selector: 'node[type="Incident"]', style: { 'background-color': '#ef4444', 'shape': 'rectangle' } },
                    { selector: 'node[type="Equipment"]', style: { 'background-color': '#3b82f6', 'shape': 'hexagon' } },
                    { selector: 'node[type="Location"]', style: { 'background-color': '#10b981', 'shape': 'diamond' } },
                    { selector: 'node[type="Hazard"]', style: { 'background-color': '#f59e0b', 'shape': 'triangle' } },
                    { selector: 'edge', style: { 'width': 2, 'line-color': 'rgba(255,255,255,0.2)', 'target-arrow-color': 'rgba(255,255,255,0.2)', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '8px', 'color': '#94a3b8', 'text-rotation': 'autorotate', 'text-margin-y': -10 } }
                  ]}
                  cy={(cy) => { setCy(cy); }}
                />
              </div>
            </div>

            {/* Timeline */}
            <div className="panel surface-panel" style={{ height: 400, overflowY: 'auto' }} id="incident-timeline">
              <div className="panel-header"><h3>Incident Timeline</h3></div>
              <div className="panel-body">
                {stateData && (stateData && stateData.reports && stateData.reports.length > 0) ? (
                  <div className="timeline">
                    {(stateData && stateData.reports ? stateData.reports.slice().reverse() : []).map(r => (
                      <div key={r.report.id} className={`timeline-item ${r.is_precursor ? 'precursor' : ''}`}>
                        <div className="timeline-date">{new Date(r.report.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - {r.report.id}</div>
                        <div style={{ fontSize: '0.9rem' }}>{r.report.text}</div>
                      </div>
                    ))}
                  </div>
                ) : <div className="empty-state">Timeline empty</div>}
              </div>
            </div>
          </div>
        )}

        
        {/* ═══ REPORTS TAB ═══ */}
        {activeTab === 'Reports' && (
          <div className="dashboard-grid">
            <div className="panel surface-panel col-span-3" style={{ overflowY: 'auto', maxHeight: '80vh' }}>
              <div className="panel-header">
                <h3>All Processed Reports ({stateData ? stateData.total_reports : 0})</h3>
              </div>
              <div className="panel-body">
                {stateData && stateData.reports && stateData.reports.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {stateData.reports.slice().reverse().map((r) => (
                      <div key={r.report.id} style={{
                        padding: 16,
                        borderRadius: 8,
                        border: r.is_precursor ? '1px solid var(--critical)' : '1px solid var(--border)',
                        background: r.is_precursor ? 'rgba(239,68,68,0.05)' : 'rgba(0,0,0,0.2)'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                          <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                            {r.report.id} - {new Date(r.report.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                          </div>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <span className="tag incident">{r.report_class}</span>
                            <span style={{
                              padding: '4px 12px', borderRadius: 16, fontSize: '0.8rem', fontWeight: 700,
                              background: r.risk_data.score >= 70 ? 'rgba(239,68,68,0.2)' : r.risk_data.score >= 40 ? 'rgba(245,158,11,0.2)' : 'rgba(34,197,94,0.2)',
                              color: r.risk_data.score >= 70 ? 'var(--critical)' : r.risk_data.score >= 40 ? 'var(--warning)' : 'var(--safe)',
                              border: `1px solid ${r.risk_data.score >= 70 ? 'var(--critical)' : r.risk_data.score >= 40 ? 'var(--warning)' : 'var(--safe)'}`
                            }}>{r.risk_data.score}/100</span>
                            {r.is_precursor && <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--critical)' }}>PRECURSOR</span>}
                          </div>
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 8, fontStyle: 'italic' }}>
                          "{r.report.text}"
                        </div>
                        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 }}>
                          {r.extracted_entities.equipment.map(e => <span key={e} className="tag equipment">{e}</span>)}
                          {r.extracted_entities.hazards.map(e => <span key={e} className="tag hazard">{e.replace('_', ' ')}</span>)}
                          {r.extracted_entities.locations.map(e => <span key={e} className="tag location">{e}</span>)}
                        </div>
                        {r.risk_data.deltas && Object.keys(r.risk_data.deltas).length > 0 && (
                          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', fontSize: '0.75rem' }}>
                            {Object.entries(r.risk_data.deltas).map(([k,v]) => (
                              <span key={k} style={{ padding: '2px 8px', borderRadius: 4, background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)', color: 'var(--warning)' }}>+{v} {k}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : <div className="empty-state">No reports loaded yet - click Load next report</div>}
              </div>
            </div>
          </div>
        )}

                {/* ═══ EVENT GRAPH TAB ═══ */}
        {activeTab === 'Event Graph' && (
          <div className="dashboard-grid">
            <div className="panel surface-panel col-span-3" style={{ height: 500 }}>
              <div className="panel-header"><h3>Precursor Chain (Temporal Knowledge Graph)</h3></div>
              <div className="panel-body" style={{ padding: 0 }}>
                {graphElements.length > 0 ? (
                  <CytoscapeComponent
                    elements={graphElements}
                    style={{ width: '100%', height: '100%' }}
                    stylesheet={[
                      { selector: 'node', style: { 'background-color': '#3b82f6', 'label': 'data(label)', 'color': '#fff', 'text-valign': 'center', 'text-outline-width': 2, 'text-outline-color': '#0f172a', 'font-size': '11px', 'width': 40, 'height': 40 } },
                      { selector: 'node[type="Incident"]', style: { 'background-color': '#ef4444', 'shape': 'rectangle', 'width': 50, 'height': 30 } },
                      { selector: 'node[type="Equipment"]', style: { 'background-color': '#3b82f6', 'shape': 'ellipse', 'width': 45, 'height': 45 } },
                      { selector: 'node[type="Location"]', style: { 'background-color': '#10b981', 'shape': 'ellipse', 'width': 40, 'height': 40 } },
                      { selector: 'node[type="Hazard"]', style: { 'background-color': '#f59e0b', 'shape': 'ellipse', 'width': 35, 'height': 35 } },
                      { selector: 'edge', style: { 'width': 1.5, 'line-color': 'rgba(255,255,255,0.3)', 'target-arrow-color': 'rgba(255,255,255,0.3)', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '7px', 'color': '#94a3b8', 'text-rotation': 'autorotate', 'text-margin-y': -8 } }
                    ]}
                    layout={{ name: 'concentric', animate: true, padding: 50, minNodeSpacing: 80, concentric: function(node) { return node.degree(); }, levelWidth: function() { return 2; } }}
                    cy={(cy) => { setCy(cy); }}
                  />
                ) : <div className="empty-state">No graph data yet — load some reports first</div>}
              </div>
            </div>
            
            {/* Graph Legend */}
            <div className="panel surface-panel col-span-3">
              <div className="panel-header"><h3>Graph Legend</h3></div>
              <div className="panel-body" style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
                {[
                  ['🔴 Rectangle', 'Incident Reports', '#ef4444'],
                  ['🔵 Hexagon', 'Equipment', '#3b82f6'],
                  ['🟢 Diamond', 'Locations', '#10b981'],
                  ['🟡 Triangle', 'Hazards', '#f59e0b'],
                  ['→ Arrows', 'Relationships (INVOLVES, OCCURRED_AT, CAUSED_BY)', 'rgba(255,255,255,0.3)'],
                ].map(([icon, desc, color]) => (
                  <div key={desc} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: '0.85rem' }}>{icon}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{desc}</span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Graph Stats */}
            <div className="panel surface-panel col-span-3">
              <div className="panel-header"><h3>Graph Statistics</h3></div>
              <div className="panel-body" style={{ display: 'flex', gap: 24 }}>
                {[
                  ['Total Nodes', graphElements.filter(e => e.data && e.data.source === undefined).length, 'var(--primary)'],
                  ['Total Edges', graphElements.filter(e => e.data && e.data.source !== undefined).length, 'var(--warning)'],
                  ['Reports Loaded', stateData ? stateData.total_reports : 0, 'var(--safe)'],
                  ['Precursors', stateData ? stateData.reports.filter(r => r.is_precursor).length : 0, 'var(--critical)'],
                ].map(([label, value, color]) => (
                  <div key={label} style={{ flex: 1, textAlign: 'center', padding: 20, background: 'var(--bg-surface2)', borderRadius: 8 }}>
                    <div style={{ fontSize: '2.5rem', fontWeight: 800, color }}>{value}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>{label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

{/* ═══ ANALYTICS TAB ═══ */}
        {activeTab === 'Analytics' && (
          <div className="dashboard-grid" id="analytics-panel">
            {/* Risk Trend Sparkline */}
            <div className="panel surface-panel col-span-3">
              <div className="panel-header"><h3>📈 Risk Score Trend</h3></div>
              <div className="panel-body">
                {analytics && analytics.risk_trend.length > 0 ? (
                  <div>
                    <RiskSparkline data={analytics.risk_trend} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      <span>{analytics.risk_trend[0]?.id}</span>
                      <span>{analytics.risk_trend[analytics.risk_trend.length - 1]?.id}</span>
                    </div>
                  </div>
                ) : <div className="empty-state">No data yet — load some reports first</div>}
              </div>
            </div>

            {/* Location Heatmap */}
            <div className="panel surface-panel">
              <div className="panel-header"><h3>📍 Location Distribution</h3></div>
              <div className="panel-body">
                {analytics ? <BarChart data={analytics.location_distribution} title="" color="var(--safe)" /> : <div className="empty-state">Loading...</div>}
              </div>
            </div>

            {/* Equipment Frequency */}
            <div className="panel surface-panel">
              <div className="panel-header"><h3>⚙️ Equipment Frequency</h3></div>
              <div className="panel-body">
                {analytics ? <BarChart data={analytics.equipment_frequency} title="" color="var(--primary)" /> : <div className="empty-state">Loading...</div>}
              </div>
            </div>

            {/* Hazard Distribution */}
            <div className="panel surface-panel">
              <div className="panel-header"><h3>⚠️ Hazard Types</h3></div>
              <div className="panel-body">
                {analytics ? <BarChart data={analytics.hazard_distribution} title="" color="var(--warning)" /> : <div className="empty-state">Loading...</div>}
              </div>
            </div>

            {/* Location Heatmap */}
            <div className="panel surface-panel col-span-3">
              <div className="panel-header"><h3>🗺️ Facility Location Heatmap — Duliajan, Assam</h3></div>
              <div className="panel-body" style={{ padding: 0 }}>
                <LocationMap analytics={analytics} />
              </div>
            </div>

            {/* Summary Cards */}
            <div className="panel surface-panel col-span-3">
              <div className="panel-header"><h3>Summary</h3></div>
              <div className="panel-body" style={{ display: 'flex', gap: 24 }}>
                {[
                  ['Total Reports', analytics?.total_reports || 0, 'var(--primary)'],
                  ['Precursors Detected', analytics?.precursors_detected || 0, 'var(--critical)'],
                  ['Unique Locations', analytics ? Object.keys(analytics.location_distribution).length : 0, 'var(--safe)'],
                  ['Equipment Types', analytics ? Object.keys(analytics.equipment_frequency).length : 0, 'var(--warning)'],
                ].map(([label, value, color]) => (
                  <div key={label} style={{ flex: 1, textAlign: 'center', padding: 20, background: 'var(--bg-surface2)', borderRadius: 8 }}>
                    <div style={{ fontSize: '2.5rem', fontWeight: 800, color }}>{value}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>{label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
      {/* Chat Widget */}
      <ChatWidget />

      {/* ── Mobile Bottom Tab Bar ──────────────────── */}
      <div className="mobile-tab-bar">
        <div className="mobile-tab-bar-inner">
          {['Dashboard', 'Reports', 'Analytics', 'Event Graph'].map(tab => (
            <div
              key={tab}
              className={`mobile-tab-item ${activeTab === tab ? 'active' : ''}`}
              onClick={() => {
                setActiveTab(tab);
                if (tab === 'Analytics') loadAnalytics();
              }}
            >
              <span className="mobile-tab-icon">
                {tab === 'Dashboard' && '◇'}
                {tab === 'Reports' && '▤'}
                {tab === 'Analytics' && '📊'}
                {tab === 'Event Graph' && '⬡'}
              </span>
              <span>{tab === 'Event Graph' ? 'Graph' : tab}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Mobile Action Bar ──────────────────────── */}
      <div className="mobile-action-bar">
        <button className="btn primary" onClick={processNext} disabled={processing}>
          {processing ? '...' : '＋ Load Report'}
        </button>
        <button className="btn secondary" onClick={() => setShowMobileInput(true)}>
          ✏️ Type Report
        </button>
        <button onClick={handleLogout} style={{ background: 'none', border: '1px solid rgba(239,68,68,0.3)', color: 'var(--critical)', padding: '6px 10px', borderRadius: 8, fontSize: '0.7rem', cursor: 'pointer', fontWeight: 600 }}>
          Sign Out
        </button>
      </div>

      {/* ── Mobile Custom Input Modal ───────────────── */}
      {showMobileInput && (
        <div className="mobile-input-overlay" onClick={() => setShowMobileInput(false)}>
          <div className="mobile-input-modal" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ fontSize: '1rem' }}>✏️ Type Safety Report</h3>
              <button onClick={() => setShowMobileInput(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>
            </div>
            <textarea
              className="mobile-custom-input"
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              placeholder='Describe the safety incident...'
              rows={5}
              style={{ width: '100%', padding: 12, borderRadius: 8, background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', color: 'var(--text-main)', fontFamily: 'inherit', fontSize: '0.9rem', resize: 'vertical', marginBottom: 12 }}
            />
            <button
              className="btn primary"
              onClick={() => { submitCustomReport(); setShowMobileInput(false); }}
              disabled={submitting || !customText.trim()}
              style={{ width: '100%', padding: 12 }}
            >
              {submitting ? 'Analyzing...' : '🔍 Analyze Report'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
