import React, { useState, useEffect } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';

function App() {
  const [stateData, setStateData] = useState(null);
  const [currentState, setCurrentState] = useState(null);
  const [graphElements, setGraphElements] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [simResults, setSimResults] = useState("Select an intervention to see predicted risk trajectory.");
  const [cy, setCy] = useState(null);
  const [activeTab, setActiveTab] = useState('Dashboard');

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
        <div style={{ fontSize: '0.65rem', color: 'var(--primary)', letterSpacing: '2px', marginBottom: '40px', paddingLeft: '36px', fontWeight: 'bold' }}>
          SIF PRECURSOR INTELLIGENCE
        </div>
        
        <div className="nav-menu">
          <a href="#" className={`nav-item ${activeTab === 'Dashboard' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Dashboard', null)}>🛡 Overview</a>
          <a href="#" className={`nav-item ${activeTab === 'Reports' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Reports', null)}>📄 Reports</a>
          <a href="#" className={`nav-item ${activeTab === 'Precursors' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Precursors', null)}>🚨 Precursors</a>
          <a href="#" className={`nav-item ${activeTab === 'Event Graph' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Event Graph', null)}>🕸 Event Graph</a>
        </div>
        
        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button className="btn primary" onClick={processNext} disabled={processing} style={{ padding: '16px', fontSize: '1.05rem', letterSpacing: '1px', fontWeight: 800 }}>
            {processing ? 'ANALYZING...' : '＋ LOAD NEXT REPORT'}
          </button>
          <button className="btn secondary" onClick={resetSimulation}>
            Reset Timeline
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="topbar">
          <h2>Command Center</h2>
          <div style={{ display: 'flex', gap: 16 }}>
            <div className="mode-badge">
              ● SIMULATION MODE
            </div>
            <div className="status-indicator">
              <div className="pulse"></div>
              AI ENGINE ONLINE
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="dashboard-grid">
          
          {/* Main Risk Hero Panel */}
          <div className="panel surface-panel col-span-2">
            <div className="panel-header">
              <h3>SAFETY RISK</h3>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 700, letterSpacing: '1px' }}>ACTIVE PRECURSOR STATUS</div>
            </div>
            <div className="panel-body" style={{ display: 'flex', gap: 20 }}>
              {currentState ? (
                <>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <div className={`risk-circle ${currentState.is_precursor ? 'critical' : (currentState.risk_data.score >= 40 ? 'warning' : 'safe')}`}>
                      {currentState.risk_data.score}
                    </div>
                    <div className={`risk-status-text ${currentState.is_precursor ? 'critical' : (currentState.risk_data.score >= 40 ? 'warning' : 'safe')}`}>
                      {currentState.is_precursor ? '🚨 CRITICAL' : (currentState.risk_data.score >= 40 ? 'WARNING' : 'NORMAL')}
                    </div>
                    <div className={`risk-trend ${currentState.risk_data.trajectory.toLowerCase()}`}>
                      {currentState.risk_data.trajectory === 'ESCALATING' ? '▲' : (currentState.risk_data.trajectory === 'DECREASING' ? '▼' : '▬')} {currentState.risk_data.trajectory} {currentState.risk_data.trajectory === 'ESCALATING' && '+'}
                    </div>
                  </div>
                  <div style={{ flex: 1.5, borderLeft: '1px solid var(--border)', paddingLeft: 30, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    {currentState.is_precursor && (
                      <div style={{ marginBottom: 16 }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 700, letterSpacing: '1px' }}>SIF PATHWAY DETECTED</div>
                        <div style={{ display: 'inline-block', padding: '6px 12px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid var(--critical)', borderRadius: '4px', color: 'var(--critical)', fontWeight: 'bold' }}>
                          {currentState.risk_data.sif_category}
                        </div>
                      </div>
                    )}
                    <div style={{ marginBottom: 16 }}>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 700, letterSpacing: '1px' }}>PRIMARY TARGET</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--text-main)' }}>
                        {currentState.extracted_entities.equipment[0] || 'Unspecified Location'}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 700, letterSpacing: '1px' }}>RECOMMENDED ACTION</div>
                      <ul style={{ paddingLeft: 20, color: 'var(--warning)', fontWeight: 600 }}>
                        {currentState.risk_data.evidence.length > 0 ? (
                           <li>Verify {currentState.extracted_entities.equipment[0] || 'area'} safety protocol</li>
                        ) : <li>Monitor for further changes</li>}
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
              <h3>SYSTEM INTELLIGENCE</h3>
            </div>
            <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Reports Analyzed</span>
                <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{stateData ? stateData.total_reports : 0}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Entities Linked</span>
                <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{graphElements.length}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Active Precursors</span>
                <span style={{ fontWeight: 'bold', fontSize: '1.1rem', color: precursors > 0 ? 'var(--critical)' : 'var(--safe)' }}>{precursors}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Unresolved Actions</span>
                <span style={{ fontWeight: 'bold', fontSize: '1.1rem', color: unresolved > 0 ? 'var(--warning)' : 'inherit' }}>{unresolved}</span>
              </div>
              
              <div style={{ marginTop: 'auto', paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button className="btn secondary" style={{ flex: 1, padding: '12px', fontSize: '0.8rem', letterSpacing: '1px' }} onClick={() => simulateIntervention('delay')} disabled={!currentState}>
                    [ DELAY ACTION ]
                  </button>
                  <button className="btn safe" style={{ flex: 1, padding: '12px', fontSize: '0.8rem', letterSpacing: '1px' }} onClick={() => simulateIntervention('resolve_action')} disabled={!currentState}>
                    [ MARK COMPLETE ]
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
              <h3>LATEST PROCESSED SIGNAL</h3>
            </div>
            <div className="panel-body">
              {currentState ? (
                <>
                  <div style={{ marginBottom: 16, fontSize: '0.95rem' }}>"{currentState.report.text}"</div>
                  <div>
                    <span className="tag" style={{ background: 'rgba(255,255,255,0.1)', borderColor: 'var(--border)' }}>🏷️ {currentState.report_class}</span>
                    {currentState.extracted_entities.equipment.map(e => <span key={e} className="tag equipment">⚙️ {e}</span>)}
                    {currentState.extracted_entities.hazards.map(e => <span key={e} className="tag hazard">⚠️ {e}</span>)}
                    {currentState.extracted_entities.locations.map(e => <span key={e} className="tag location">📍 {e}</span>)}
                  </div>
                </>
              ) : <div className="empty-state">Waiting for next report...</div>}
            </div>
          </div>

          <div className="panel surface-panel">
            <div className="panel-header">
              <h3>✨ AI REASONING</h3>
            </div>
            <div className="panel-body" style={{ background: 'rgba(34, 211, 238, 0.05)', borderLeft: '3px solid var(--primary)', overflowY: 'auto' }}>
              {currentState ? (
                <div dangerouslySetInnerHTML={{ __html: currentState.llm_explanation.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>') }} style={{ fontSize: '0.85rem', lineHeight: '1.5' }} />
              ) : <div className="empty-state">Waiting for AI...</div>}
            </div>
          </div>

          {/* Risk Trajectory Graph */}
          <div className="panel surface-panel col-span-2">
            <div className="panel-header">
              <h3>RISK TRAJECTORY</h3>
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
              <h3>WHY NOW?</h3>
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
                     <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 700, letterSpacing: '1px' }}>EVIDENCE SOURCE</div>
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
          <div className="panel surface-panel col-span-3">
            <div className="panel-header">
              <h3>PRECURSOR CHAIN (TEMPORAL GRAPH)</h3>
            </div>
            <div className="panel-body" style={{ height: 300, padding: 0 }}>
              <CytoscapeComponent 
                elements={graphElements} 
                style={{ width: '100%', height: '100%' }}
                stylesheet={[
                  {
                    selector: 'node',
                    style: {
                      'background-color': '#22D3EE',
                      'label': 'data(label)',
                      'color': '#F8FAFC',
                      'text-valign': 'center',
                      'text-outline-width': 2,
                      'text-outline-color': '#0D1B2A',
                      'font-size': '12px'
                    }
                  },
                  { selector: 'node[type="Incident"]', style: { 'background-color': '#EF4444', 'shape': 'rectangle' } },
                  { selector: 'node[type="Equipment"]', style: { 'background-color': '#22D3EE', 'shape': 'hexagon' } },
                  { selector: 'node[type="Location"]', style: { 'background-color': '#22C55E', 'shape': 'diamond' } },
                  { selector: 'node[type="Hazard"]', style: { 'background-color': '#F59E0B', 'shape': 'triangle' } },
                  {
                    selector: 'edge',
                    style: {
                      'width': 2,
                      'line-color': '#20354A',
                      'target-arrow-color': '#20354A',
                      'target-arrow-shape': 'triangle',
                      'curve-style': 'bezier',
                      'label': 'data(label)',
                      'font-size': '10px',
                      'color': '#94A3B8',
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
          <div className="panel surface-panel col-span-3" style={{ height: 300, overflowY: 'auto' }} id="incident-timeline">
            <div className="panel-header">
              <h3>INCIDENT TIMELINE</h3>
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
