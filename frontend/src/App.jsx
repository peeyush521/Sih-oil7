import React, { useState, useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';

const Typewriter = ({ text }) => {
  const [content, setContent] = useState('');
  useEffect(() => {
    setContent('');
    let i = 0;
    const cleanText = text.replace(/\*\*(.*?)\*\*/g, '$1'); // Strip markdown
    const timer = setInterval(() => {
      setContent(cleanText.slice(0, i));
      i++;
      if (i > cleanText.length) clearInterval(timer);
    }, 15);
    return () => clearInterval(timer);
  }, [text]);
  return <div style={{ fontSize: '0.85rem', lineHeight: '1.5', fontFamily: 'monospace' }}>{content}<span style={{ animation: 'blink 1s step-end infinite' }}>█</span></div>;
}

function App() {
  const [stateData, setStateData] = useState(null);
  const [currentState, setCurrentState] = useState(null);
  const [graphElements, setGraphElements] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [simResults, setSimResults] = useState("Select an intervention to see predicted risk trajectory.");
  const [cy, setCy] = useState(null);
  const [activeTab, setActiveTab] = useState('Dashboard');

  const playAlarm = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = 'square';
      osc.frequency.setValueAtTime(880, ctx.currentTime); 
      osc.frequency.setValueAtTime(660, ctx.currentTime + 0.2); 
      
      gain.gain.setValueAtTime(0.05, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.4);
      
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.4);
    } catch(e) {}
  };

  useEffect(() => {
    if (currentState?.is_precursor) {
      playAlarm();
      const interval = setInterval(playAlarm, 2000);
      return () => clearInterval(interval);
    }
  }, [currentState?.is_precursor]);

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
    } catch (e) {
      console.error(e);
    }
  };

  const fetchGraph = async () => {
    try {
      const res = await fetch('/api/graph_data');
      const data = await res.json();
      setGraphElements(data);
      if(cy) {
        cy.layout({ name: 'cose', animate: true, padding: 30 }).run();
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadState();
  }, []);

  const processNext = async () => {
    setProcessing(true);
    try {
      const res = await fetch('/api/process_next', { method: 'POST' });
      if (!res.ok) {
        if(res.status === 400) {
          alert("Simulation Complete");
        }
        return;
      }
      const data = await res.json();
      setCurrentState(data);
      await loadState();
      setSimResults("Select an intervention to see predicted risk trajectory.");
    } catch(e) {
      console.error(e);
    } finally {
      setProcessing(false);
    }
  };

  const resetSimulation = async () => {
    await fetch('/api/reset');
    await loadState();
    setSimResults("Select an intervention to see predicted risk trajectory.");
  };

  const simulateIntervention = async (action) => {
    if(!currentState) return;
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
    } catch(e) {
      console.error(e);
    }
  };

  let precursors = 0;
  let unresolved = 0;
  if(stateData) {
    stateData.reports.forEach(r => {
      if(r.is_precursor) precursors++;
      if(r.report.action_status === "Open") unresolved++;
    });
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo" style={{ marginBottom: '10px' }}>
          <div className="logo-icon">🛡️</div>
          <h1>SAFEGUARD AI</h1>
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', letterSpacing: '0.5px', marginBottom: '40px', paddingLeft: '36px', fontWeight: '500' }}>
          Industrial Safety Intelligence
        </div>
        
        <div className="nav-menu">
          <a href="#" className={`nav-item ${activeTab === 'Dashboard' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Dashboard', null)}>◇ Overview</a>
          <a href="#" className={`nav-item ${activeTab === 'Reports' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Reports', 'incident-timeline')}>▤ Reports</a>
          <a href="#" className={`nav-item ${activeTab === 'Precursors' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Precursors', 'precursor-chain-panel')}>⚠ Precursors</a>
          <a href="#" className={`nav-item ${activeTab === 'Event Graph' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Event Graph', 'precursor-chain-panel')}>◇ Event Graph</a>
        </div>
        
        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button className="btn primary" onClick={processNext} disabled={processing} style={{ padding: '12px', fontSize: '0.95rem', fontWeight: 600 }}>
            {processing ? 'Analyzing...' : '＋ Load next report'}
          </button>
          <button className="btn secondary" onClick={resetSimulation} style={{ padding: '8px', fontSize: '0.8rem', border: 'none' }}>
            Reset timeline
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className={`main-content ${currentState?.is_precursor ? 'critical-alarm-active' : ''}`}>
        <div className="topbar">
          <h2>Command Center</h2>
          <div style={{ display: 'flex', gap: 16 }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', border: '1px solid var(--border)', padding: '6px 10px', borderRadius: '4px' }}>
              <div style={{ color: 'var(--primary)', fontSize: '0.6rem', marginTop: '2px' }}>●</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: '1.2' }}>Simulation<br/>Mode</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', border: '1px solid var(--border)', padding: '6px 10px', borderRadius: '4px' }}>
              <div style={{ color: 'var(--safe)', fontSize: '0.6rem', marginTop: '2px' }}>●</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: '1.2' }}>AI Engine<br/>Online</div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="dashboard-grid">
          
          {/* Main Risk Hero Panel */}
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
                    <div style={{ marginTop: '16px', fontSize: '0.6rem', color: 'var(--text-muted)', display: 'flex', gap: '4px', alignItems: 'center', fontFamily: 'monospace' }}>
                      LOW ─ MEDIUM ─ HIGH {currentState.is_precursor ? <span style={{ color: 'var(--critical)' }}>━ CRITICAL</span> : '─ CRITICAL'}
                    </div>
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
            <div className="panel-header">
              <h3>System Intelligence</h3>
            </div>
            <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Last updated</span>
                <span style={{ fontWeight: 'bold', fontSize: '0.95rem', fontFamily: 'var(--font-mono)' }}>{new Date().toLocaleTimeString()}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Signal confidence</span>
                <span style={{ fontWeight: 'bold', fontSize: '0.95rem' }}>94%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Reports analyzed</span>
                <span style={{ fontWeight: 'bold', fontSize: '1.05rem' }}>{stateData ? stateData.total_reports : 0}</span>
              </div>
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
                  <button className="btn secondary" style={{ flex: 1, padding: '10px', fontSize: '0.85rem' }} onClick={() => simulateIntervention('delay')} disabled={!currentState}>
                    Delay action
                  </button>
                  <button className="btn safe" style={{ flex: 1, padding: '10px', fontSize: '0.85rem' }} onClick={() => simulateIntervention('resolve_action')} disabled={!currentState}>
                    ✓ Mark complete
                  </button>
                </div>
                {simResults !== "Select an intervention to see predicted risk trajectory." && (
                  <div style={{ marginTop: 12, textAlign: 'center', background: 'var(--bg-surface2)', padding: '8px', borderRadius: '4px' }}>
                    {simResults}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Latest Signal & AI Reasoning */}
          <div className="panel surface-panel col-span-2">
            <div className="panel-header">
              <h3>Latest Processed Signal</h3>
            </div>
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

          <div className="panel surface-panel">
            <div className="panel-header">
              <h3>AI Reasoning</h3>
            </div>
            <div className="panel-body" style={{ background: 'rgba(24, 198, 217, 0.02)', borderLeft: '3px solid var(--primary)', overflowY: 'auto' }}>
              {currentState ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', height: '100%' }}>
                  <div style={{ color: 'var(--text-main)', fontWeight: 600, fontSize: '0.9rem' }}>
                    Why is {currentState.extracted_entities.equipment[0] || 'the target'} high risk?
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

          {/* Risk Trajectory Graph */}
          <div className="panel surface-panel col-span-2">
            <div className="panel-header">
              <h3>Risk Trajectory</h3>
            </div>
            <div className="panel-body">
              {stateData && stateData.reports.length > 0 ? (
                <div className="trajectory-chart">
                  <div className="chart-y-axis">
                     <span>100</span>
                     <span>75</span>
                     <span>50</span>
                     <span>25</span>
                     <span>0</span>
                  </div>
                  <div className="chart-threshold" style={{ bottom: '70%' }}></div>
                  
                  {stateData.reports.map((r, i) => {
                    const total = stateData.reports.length;
                    const left = total === 1 ? '50%' : `${(i / (total - 1)) * 100}%`;
                    const bottom = `${r.risk_data.score}%`;
                    
                    // Optional line to next point
                    let lineStyle = { display: 'none' };
                    if (i < total - 1) {
                      const next = stateData.reports[i+1];
                      const w = 100 / (total - 1);
                      // This is a rough CSS line approx for visual purposes
                      lineStyle = { display: 'none' }; // Pure CSS diagonal lines are complex without SVG, skipping line connecting for precise look, keeping dots
                    }

                    return (
                      <React.Fragment key={i}>
                        <div className={`chart-point ${r.is_precursor ? 'critical' : ''}`} style={{ left, bottom }}>
                          <span style={{ position: 'absolute', top: -25, left: '50%', transform: 'translateX(-50%)', fontSize: '0.8rem', fontWeight: 'bold', color: r.is_precursor ? 'var(--critical)' : 'var(--text-main)' }}>
                            {r.risk_data.score}
                          </span>
                        </div>
                      </React.Fragment>
                    );
                  })}
                  
                  <div className="chart-x-axis">
                    {stateData.reports.map((r, i) => (
                      <span key={i}>D{i+1}</span>
                    ))}
                  </div>
                </div>
              ) : <div className="empty-state">No timeline data</div>}
            </div>
          </div>

          {/* Why Now / Evidence Breakdown */}
          <div className="panel surface-panel">
            <div className="panel-header">
              <h3>Why Now?</h3>
            </div>
            <div className="panel-body">
              {currentState && currentState.risk_data.deltas && Object.keys(currentState.risk_data.deltas).length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                  {Object.entries(currentState.risk_data.deltas).map(([factor, score]) => (
                    <div key={factor} className="evidence-bar-container">
                      <div className="evidence-bar-header">
                        <span>{factor}</span>
                        <span className="val">+{score}</span>
                      </div>
                      <div className="evidence-bar-bg">
                        <div className="evidence-bar-fill" style={{ width: `${Math.min((score / 20) * 100, 100)}%` }}></div>
                      </div>
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

          {/* Precursor Chain (Graph) */}
          <div className="panel surface-panel col-span-2" id="precursor-chain-panel" style={{ height: 400 }}>
            <div className="panel-header">
              <h3>Precursor Chain (Temporal Graph)</h3>
            </div>
            <div className="panel-body" style={{ padding: 0 }}>
              <CytoscapeComponent 
                elements={graphElements} 
                style={{ width: '100%', height: '100%' }}
                stylesheet={[
                  {
                    selector: 'node',
                    style: {
                      'background-color': '#3b82f6',
                      'label': 'data(label)',
                      'color': '#fff',
                      'text-valign': 'center',
                      'text-outline-width': 2,
                      'text-outline-color': '#0f172a',
                      'font-size': '10px'
                    }
                  },
                  { selector: 'node[type="Incident"]', style: { 'background-color': '#ef4444', 'shape': 'rectangle' } },
                  { selector: 'node[type="Equipment"]', style: { 'background-color': '#3b82f6', 'shape': 'hexagon' } },
                  { selector: 'node[type="Location"]', style: { 'background-color': '#10b981', 'shape': 'diamond' } },
                  { selector: 'node[type="Hazard"]', style: { 'background-color': '#f59e0b', 'shape': 'triangle' } },
                  {
                    selector: 'edge',
                    style: {
                      'width': 2,
                      'line-color': 'rgba(255,255,255,0.2)',
                      'target-arrow-color': 'rgba(255,255,255,0.2)',
                      'target-arrow-shape': 'triangle',
                      'curve-style': 'bezier',
                      'label': 'data(label)',
                      'font-size': '8px',
                      'color': '#94a3b8',
                      'text-rotation': 'autorotate',
                      'text-margin-y': -10
                    }
                  }
                ]}
                cy={(cy) => { setCy(cy); }}
              />
            </div>
          </div>

          {/* Incident Timeline */}
          <div className="panel surface-panel" style={{ height: 400, overflowY: 'auto' }} id="incident-timeline">
            <div className="panel-header">
              <h3>Incident Timeline</h3>
            </div>
            <div className="panel-body">
              {stateData && stateData.reports.length > 0 ? (
                <div className="timeline">
                  {stateData.reports.slice().reverse().map(r => (
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
      </div>
    </div>
  );
}

export default App;
