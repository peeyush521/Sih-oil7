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
        <div className="logo">
          <div className="logo-icon">✨</div>
          <h1>SIF Command Center</h1>
        </div>
        
        <div className="nav-menu">
          <a href="#" className={`nav-item ${activeTab === 'Dashboard' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Dashboard', null)}>Dashboard</a>
          <a href="#" className={`nav-item ${activeTab === 'Risk Investigation' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Risk Investigation', 'risk-assessment-container')}>Risk Investigation</a>
          <a href="#" className={`nav-item ${activeTab === 'Timeline' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Timeline', 'incident-timeline')}>Timeline</a>
          <a href="#" className={`nav-item ${activeTab === 'Settings' ? 'active' : ''}`} onClick={(e) => handleNavClick(e, 'Settings', null)}>Settings</a>
        </div>
        
        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button className="btn primary" onClick={processNext} disabled={processing}>
            {processing ? 'Processing...' : 'Load Next Real Report'}
          </button>
          <button className="btn secondary" onClick={resetSimulation}>
            Reset Timeline
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="topbar">
          <h2>System Overview</h2>
          <div className="status-indicator">
            <div className="pulse"></div>
            System Active
          </div>
        </div>

        {/* Stats Grid */}
        <div className="dashboard-grid">
          <div className="stat-card glass-panel">
            <h3>Total Reports</h3>
            <div className="stat-value">{stateData ? stateData.total_reports : 0}</div>
          </div>
          <div className="stat-card warning glass-panel">
            <h3>Emerging Precursors</h3>
            <div className="stat-value">{precursors}</div>
          </div>
          <div className="stat-card critical glass-panel">
            <h3>Unresolved Actions</h3>
            <div className="stat-value">{unresolved}</div>
          </div>

          {/* Alert Banner */}
          {currentState?.is_precursor && (
            <div className="col-span-3">
              <div className="alert-banner">
                <div className="alert-icon">🚨</div>
                <div className="alert-content">
                  <h3>PRECURSOR DETECTED</h3>
                  <p>High risk pattern emerging related to {currentState.extracted_entities.equipment[0] || 'recent events'}. Immediate intervention recommended.</p>
                </div>
              </div>
            </div>
          )}

          {/* Latest Signal & AI Reasoning */}
          <div className="panel glass-panel col-span-2">
            <div className="panel-header">
              <h3>Latest Processed Signal</h3>
            </div>
            <div className="panel-body">
              {currentState ? (
                <>
                  <div style={{ marginBottom: 12 }}>{currentState.report.text}</div>
                  <div>
                    <span className="tag" style={{ background: 'rgba(255,255,255,0.2)' }}>🏷️ {currentState.report_class}</span>
                    {currentState.extracted_entities.equipment.map(e => <span key={e} className="tag equipment">⚙️ {e}</span>)}
                    {currentState.extracted_entities.hazards.map(e => <span key={e} className="tag hazard">⚠️ {e}</span>)}
                    {currentState.extracted_entities.locations.map(e => <span key={e} className="tag location">📍 {e}</span>)}
                  </div>
                </>
              ) : <div className="empty-state">Waiting for next report...</div>}
            </div>
          </div>

          <div className="panel glass-panel">
            <div className="panel-header">
              <h3>✨ AI Reasoning</h3>
            </div>
            <div className="panel-body" style={{ background: 'rgba(59, 130, 246, 0.1)', borderLeft: '3px solid var(--accent)' }}>
              {currentState ? (
                <div dangerouslySetInnerHTML={{ __html: currentState.llm_explanation.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>') }} />
              ) : <div className="empty-state">Waiting for AI...</div>}
            </div>
          </div>

          {/* Risk Assessment */}
          <div className="panel glass-panel col-span-3" id="risk-assessment-container">
            <div className="panel-header">
              <h3>Deterministic Risk Assessment</h3>
              {currentState?.risk_data.sif_category && currentState.risk_data.sif_category !== "None" && (
                <div style={{ padding: '4px 8px', borderRadius: 4, background: 'rgba(255, 100, 100, 0.2)', border: '1px solid rgba(255,100,100,0.5)', fontSize: '0.8rem', fontWeight: 600, color: '#ff6b6b' }}>
                  SIF Pathway: {currentState.risk_data.sif_category}
                </div>
              )}
            </div>
            <div className="panel-body" style={{ display: 'flex', gap: 20 }}>
              {currentState ? (
                <>
                  <div style={{ flex: 1 }}>
                    <div className="risk-score-container">
                      <div className={`risk-circle ${currentState.risk_data.score >= 70 ? 'critical' : (currentState.risk_data.score >= 40 ? 'warning' : 'safe')}`}>
                        {currentState.risk_data.score}
                      </div>
                      <div>
                        <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Risk Trajectory</div>
                        <div className={`risk-trend ${currentState.risk_data.trajectory.toLowerCase()}`}>
                          {currentState.risk_data.trajectory === 'ESCALATING' ? '↗' : (currentState.risk_data.trajectory === 'DECREASING' ? '↘' : '→')} {currentState.risk_data.trajectory}
                        </div>
                      </div>
                    </div>
                    <h4 style={{ color: 'var(--text-muted)', marginBottom: 8 }}>Evidence</h4>
                    <ul style={{ paddingLeft: 20 }}>
                      {currentState.risk_data.evidence.length > 0 ? currentState.risk_data.evidence.map((e, i) => <li key={i}>{e}</li>) : <li>No specific precursor evidence</li>}
                    </ul>
                  </div>
                  <div style={{ flex: 1, paddingLeft: 20, borderLeft: '1px solid var(--border)' }}>
                    <h4 style={{ color: 'var(--text-muted)', marginBottom: 12 }}>Why did risk change?</h4>
                    <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: 12, fontSize: '0.9rem' }}>
                      {currentState.risk_data.deltas && Object.keys(currentState.risk_data.deltas).length > 0 ? (
                        Object.entries(currentState.risk_data.deltas).map(([k, v]) => (
                          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                            <span>{k}</span>
                            <span style={{ color: '#ff6b6b', fontWeight: 'bold' }}>+{v}</span>
                          </div>
                        ))
                      ) : <div>No significant compounding factors.</div>}
                      <div style={{ borderTop: '1px solid var(--border)', marginTop: 8, paddingTop: 8, display: 'flex', justifyContent: 'space-between', fontWeight: 'bold' }}>
                        <span>Total Compounding Score</span>
                        <span style={{ color: '#ff6b6b' }}>
                          +{Object.values(currentState.risk_data.deltas || {}).reduce((a, b) => a + b, 0)}
                        </span>
                      </div>
                    </div>
                  </div>
                </>
              ) : <div className="empty-state">No risk data available</div>}
            </div>
          </div>

          {/* Graph & Timeline */}
          <div className="panel glass-panel col-span-2" style={{ height: 400 }}>
            <div className="panel-header">
              <h3>Temporal Safety Graph</h3>
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

          <div className="panel glass-panel" style={{ height: 400, overflowY: 'auto' }} id="incident-timeline">
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

          {/* Intervention Simulator */}
          <div className="panel glass-panel col-span-3">
            <div className="panel-header">
              <h3>Intervention Impact Simulation</h3>
            </div>
            <div className="panel-body" style={{ display: 'flex', gap: 20 }}>
              <div style={{ flex: 1, display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                <button className="btn secondary" onClick={() => simulateIntervention('delay')}>Delay Action</button>
                <button className="btn safe" onClick={() => simulateIntervention('resolve_action')}>Mark Corrective Action Complete</button>
              </div>
              <div style={{ flex: 1, background: 'rgba(0,0,0,0.2)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {simResults}
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;
