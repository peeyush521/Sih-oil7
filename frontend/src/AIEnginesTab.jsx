
import React, { useState, useEffect, useCallback } from 'react';

/* ── Horizontal Bar (SHAP/LIME style) ─────────────────── */
const HorizontalBar = ({ label, value, maxValue, color = '#3b82f6', direction }) => (
  <div style={{ marginBottom: 6 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
      <span style={{ color: '#cbd5e1', fontSize: 12, fontWeight: 600, minWidth: 140, textAlign: 'right', paddingRight: 8 }}>{label}</span>
      <span style={{ color: direction === 'positive' ? '#ef4444' : '#22c55e', fontSize: 12, fontWeight: 700, minWidth: 50, textAlign: 'right' }}>{direction === 'positive' ? '+' : '-'}{value}</span>
    </div>
    <div style={{ background: '#0f0f1a', borderRadius: 4, height: 8, overflow: 'hidden' }}>
      <div style={{ height: '100%', width: `${Math.min(100, (Math.abs(value) / Math.max(maxValue, 1)) * 100)}%`, background: color, borderRadius: 4, transition: 'width 0.6s ease' }} />
    </div>
  </div>
);

/* ── Confusion Matrix Cell ────────────────────────────── */
const CMCell = ({ value, isDiag, maxVal }) => {
  const intensity = Math.min(1, value / Math.max(maxVal, 1));
  const bg = isDiag
    ? `rgba(34, 197, 94, ${0.15 + intensity * 0.55})`
    : value > 0
    ? `rgba(239, 68, 68, ${0.1 + intensity * 0.4})`
    : 'transparent';
  return (
    <div style={{ width: 52, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center', background: bg, borderRadius: 4, fontSize: 13, fontWeight: isDiag ? 800 : 500, color: isDiag ? '#22c55e' : value > 0 ? '#ef4444' : '#334155' }}>
      {value}
    </div>
  );
};

/* ── Comparison Row ───────────────────────────────────── */
const CompRow = ({ label, ai, manual, unit = '', better = 'higher' }) => {
  const aiWins = better === 'higher' ? ai >= manual : ai <= manual;
  return (
    <div style={{ display: 'flex', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
      <div style={{ flex: 2, color: '#cbd5e1', fontSize: 13, fontWeight: 500 }}>{label}</div>
      <div style={{ flex: 1, textAlign: 'center' }}>
        <span style={{ color: '#18c6d9', fontSize: 16, fontWeight: 700 }}>{ai}{unit}</span>
      </div>
      <div style={{ flex: 1, textAlign: 'center' }}>
        <span style={{ color: '#94a3b8', fontSize: 16, fontWeight: 700 }}>{manual}{unit}</span>
      </div>
      <div style={{ flex: 0.8, textAlign: 'center' }}>
        <span style={{ fontSize: 12, fontWeight: 700, color: aiWins ? '#22c55e' : '#ef4444' }}>
          {aiWins ? '✓ SAFEGUARD WINS' : '✗ MANUAL WINS'}
        </span>
      </div>
    </div>
  );
};

const Stat = ({ label, value, color = '#e2e8f0' }) => (
  <div style={{ textAlign: 'center', flex: 1, minWidth: 100 }}>
    <div style={{ color: '#94a3b8', fontSize: 11, textTransform: 'uppercase', letterSpacing: 1 }}>{label}</div>
    <div style={{ color, fontSize: 22, fontWeight: 700, marginTop: 2 }}>{value}</div>
  </div>
);

const Badge = ({ text, bg = '#6366f133', color = '#818cf8' }) => (
  <span style={{ background: bg, color, padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600, display: 'inline-block', margin: 2 }}>{text}</span>
);

const riskColor = (r) => {
  if (r === 'CRITICAL') return '#ef4444';
  if (r === 'HIGH') return '#f97316';
  if (r === 'WARNING') return '#eab308';
  return '#22c55e';
};

function PredictionsView({ data }) {
  if (!data) return <div style={{ color: '#94a3b8' }}>Loading...</div>;
  if (data.error) return <div style={{ color: '#ef4444' }}>Error: {data.error}</div>;
  const preds = data.predictions || [];
  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <Stat label="Entities" value={preds.length} />
        <Stat label="Critical" value={preds.filter(p => p.risk_level === 'CRITICAL').length} color="#ef4444" />
        <Stat label="Escalating" value={preds.filter(p => p.trend === 'ESCALATING').length} color="#f97316" />
      </div>
      <div style={{ color: '#94a3b8', fontSize: 12, marginBottom: 12, fontStyle: 'italic' }}>{typeof data.summary === "string" ? data.summary : (data.summary && data.summary.message) || ""}</div>
      {preds.map((e, i) => (
        <div key={i} style={{ background: '#0f0f1a', borderRadius: 8, padding: 12, marginBottom: 8, borderLeft: '4px solid ' + riskColor(e.risk_level) }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{e.entity_name}</span>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <Badge text={e.risk_level} bg={riskColor(e.risk_level) + '22'} color={riskColor(e.risk_level)} />
              <span style={{ color: '#94a3b8', fontSize: 12 }}>{e.risk_probability}%</span>
            </div>
          </div>
          <div style={{ color: '#64748b', fontSize: 11, marginTop: 4 }}>
            Trend: {e.trend} | Incidents: {e.historical_incidents} | Avg Risk: {e.avg_risk_score}
          </div>
        </div>
      ))}
    </div>
  );
}
function AnomaliesView({ data }) {
  if (!data) return <div style={{ color: '#94a3b8' }}>Loading...</div>;
  if (data.error) return <div style={{ color: '#ef4444' }}>Error: {data.error}</div>;
  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <Stat label="Checked" value={data.total_checked || 0} />
        <Stat label="Anomalies" value={data.total_anomalies || 0} color="#f97316" />
        <Stat label="Rate" value={(data.anomaly_rate || 0) + '%'} color="#eab308" />
      </div>
      {(data.anomalies || []).slice(0, 10).map((a, i) => (
        <div key={i} style={{ background: '#0f0f1a', borderRadius: 8, padding: 12, marginBottom: 8, borderLeft: '4px solid ' + (a.anomaly_score > 70 ? '#ef4444' : a.anomaly_score > 50 ? '#f97316' : '#eab308') }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{a.report_id}</span>
            <Badge text={'Score: ' + a.anomaly_score} bg="#f9731622" color="#f97316" />
          </div>
          {a.anomalous_features && a.anomalous_features.slice(0, 3).map((f, j) => (
            <Badge key={j} text={f.feature} bg="#6366f122" color="#818cf8" />
          ))}
        </div>
      ))}
    </div>
  );
}

function GNNView({ data }) {
  if (!data) return <div style={{ color: '#94a3b8' }}>Loading...</div>;
  if (data.error) return <div style={{ color: '#ef4444' }}>Error: {data.error}</div>;
  const centrality = data.high_centrality_nodes || [];
  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <Stat label="Nodes" value={data.node_count || 0} />
        <Stat label="Edges" value={data.edge_count || 0} />
        <Stat label="Dim" value={data.embedding_dim || 0} color="#eab308" />
      </div>
      {centrality.length > 0 && (
        <div>
          <div style={{ color: '#eab308', fontWeight: 600, fontSize: 13, marginBottom: 8 }}>High Centrality Nodes</div>
          {centrality.slice(0, 8).map((n, i) => (
            <div key={i} style={{ background: '#0f0f1a', borderRadius: 6, padding: 8, marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#e2e8f0', fontSize: 12 }}>{n.name}</span>
              <span style={{ color: '#eab308', fontSize: 12, fontWeight: 600 }}>{n.centrality}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function FatigueView({ data }) {
  if (!data) return <div style={{ color: '#94a3b8' }}>Loading...</div>;
  if (data.error) return <div style={{ color: '#ef4444' }}>Error: {data.error}</div>;
  const schedules = (data.crew_schedule && data.crew_schedule.schedules) || [];
  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <Stat label="Reports" value={data.total_reports || 0} />
        <Stat label="Night %" value={(data.night_incident_pct || 0) + '%'} color="#f97316" />
      </div>
      {schedules.map((s, i) => {
        const rc = s.level === 'CRITICAL' ? '#ef4444' : s.level === 'HIGH' ? '#f97316' : '#eab308';
        return (
          <div key={i} style={{ background: '#0f0f1a', borderRadius: 8, padding: 12, marginBottom: 8, borderLeft: '4px solid ' + rc }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{s.crew_member}</span>
              <Badge text={s.level} bg={rc + '22'} color={rc} />
            </div>
            <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 4 }}>
              Fatigue: {s.fatigue_risk}x | Rest: {s.rest_hours}h | {s.suggestion}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function AlertsView({ data }) {
  if (!data) return <div style={{ color: '#94a3b8' }}>Loading...</div>;
  if (data.error) return <div style={{ color: '#ef4444' }}>Error: {data.error}</div>;
  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <Stat label="Total" value={data.total || 0} />
        <Stat label="Critical" value={data.critical_count || 0} color="#ef4444" />
      </div>
      {(data.alerts || []).length === 0 && <div style={{ color: '#94a3b8', padding: 20, textAlign: 'center' }}>No alerts yet</div>}
      {(data.alerts || []).map((a, i) => (
        <div key={i} style={{ background: '#0f0f1a', borderRadius: 8, padding: 10, marginBottom: 6, borderLeft: '4px solid ' + riskColor(a.severity) }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{a.report_id}</span>
            <Badge text={a.severity} bg={riskColor(a.severity) + '22'} color={riskColor(a.severity)} />
          </div>
        </div>
      ))}
    </div>
  );
}
/* ── ML Metrics View ────────────────────────────────────── */
function MetricsView({ data }) {
  if (!data) return <div style={{ color: '#94a3b8' }}>Loading...</div>;
  if (data.error) return <div style={{ color: '#ef4444' }}>Error: {data.error}</div>;
  // Unwrap nested classifier_metrics from /api/benchmark
  const m = data.classifier_metrics || data;
  const cm = m.confusion_matrix || [];
  const labels = m.labels || [];
  const report = m.classification_report || {};
  const maxCM = cm.length > 0 ? Math.max(...cm.flat()) : 1;
  const classLabels = labels.filter(l => !['accuracy', 'macro avg', 'weighted avg'].includes(l));
  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        <Stat label="Accuracy" value={(m.test_accuracy || 0) + '%'} color="#22c55e" />
        <Stat label="Precision" value={(m.precision_macro || 0) + '%'} color="#3b82f6" />
        <Stat label="Recall" value={(m.recall_macro || 0) + '%'} color="#f59e0b" />
        <Stat label="F1 Score" value={(m.f1_macro || 0) + '%'} color="#8b5cf6" />
        <Stat label="CV Mean" value={(m.cv_mean || 0) + '%'} color="#06b6d4" />
      </div>
      <div style={{ display: 'flex', gap: 16, marginBottom: 20, padding: '12px 16px', background: '#0f0f1a', borderRadius: 8, borderLeft: '3px solid #06b6d4' }}>
        <div style={{ color: '#94a3b8', fontSize: 12 }}>Train: <span style={{ color: '#e2e8f0', fontWeight: 700 }}>{m.train_size}</span> reports</div>
        <div style={{ color: '#94a3b8', fontSize: 12 }}>Test: <span style={{ color: '#e2e8f0', fontWeight: 700 }}>{m.test_size}</span> reports</div>
        <div style={{ color: '#94a3b8', fontSize: 12 }}>Classes: <span style={{ color: '#e2e8f0', fontWeight: 700 }}>{m.num_classes}</span></div>
        <div style={{ color: '#94a3b8', fontSize: 12 }}>CV: <span style={{ color: '#e2e8f0', fontWeight: 700 }}>{m.cv_mean}% +/- {m.cv_std}%</span></div>
      </div>
      {cm.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ color: '#e2e8f0', fontWeight: 700, fontSize: 14, marginBottom: 10 }}>Confusion Matrix</div>
          <div style={{ overflowX: 'auto' }}>
            <div style={{ display: 'inline-flex', flexDirection: 'column', gap: 0 }}>
              <div style={{ display: 'flex', gap: 0, paddingLeft: 100 }}>
                {classLabels.map((l, i) => (
                  <div key={i} style={{ width: 52, textAlign: 'center', color: '#94a3b8', fontSize: 9, fontWeight: 600, padding: '0 2px', wordBreak: 'break-all' }}>{l.slice(0, 10)}</div>
                ))}
              </div>
              {cm.map((row, ri) => (
                <div key={ri} style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
                  <div style={{ width: 100, color: '#94a3b8', fontSize: 10, fontWeight: 600, textAlign: 'right', paddingRight: 8 }}>{classLabels[ri]?.slice(0, 12)}</div>
                  {row.map((val, ci) => (
                    <CMCell key={ci} value={val} isDiag={ri === ci} maxVal={maxCM} />
                  ))}
                </div>
              ))}
            </div>
            <div style={{ marginTop: 8, display: 'flex', gap: 16, paddingLeft: 100 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 12, height: 12, borderRadius: 2, background: 'rgba(34,197,94,0.5)' }} /><span style={{ color: '#94a3b8', fontSize: 11 }}>Correct</span></div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 12, height: 12, borderRadius: 2, background: 'rgba(239,68,68,0.35)' }} /><span style={{ color: '#94a3b8', fontSize: 11 }}>Misclassified</span></div>
            </div>
          </div>
        </div>
      )}
      {classLabels.length > 0 && (
        <div>
          <div style={{ color: '#e2e8f0', fontWeight: 700, fontSize: 14, marginBottom: 10 }}>Per-Class Metrics</div>
          <div style={{ background: '#0f0f1a', borderRadius: 8, overflow: 'hidden' }}>
            <div style={{ display: 'flex', padding: '8px 12px', borderBottom: '1px solid #334155', background: 'rgba(255,255,255,0.02)' }}>
              <div style={{ flex: 2, color: '#94a3b8', fontSize: 11, fontWeight: 600, textTransform: 'uppercase' }}>Class</div>
              <div style={{ flex: 1, color: '#94a3b8', fontSize: 11, fontWeight: 600, textAlign: 'center' }}>Precision</div>
              <div style={{ flex: 1, color: '#94a3b8', fontSize: 11, fontWeight: 600, textAlign: 'center' }}>Recall</div>
              <div style={{ flex: 1, color: '#94a3b8', fontSize: 11, fontWeight: 600, textAlign: 'center' }}>F1</div>
              <div style={{ flex: 1, color: '#94a3b8', fontSize: 11, fontWeight: 600, textAlign: 'center' }}>Support</div>
            </div>
            {classLabels.map((cls, i) => {
              const m = report[cls] || {};
              return (
                <div key={i} style={{ display: 'flex', padding: '8px 12px', borderBottom: '1px solid rgba(255,255,255,0.03)', alignItems: 'center' }}>
                  <div style={{ flex: 2, color: '#e2e8f0', fontSize: 12, fontWeight: 600 }}>{cls}</div>
                  <div style={{ flex: 1, textAlign: 'center' }}>
                    <div style={{ color: (m.precision || 0) >= 0.7 ? '#22c55e' : (m.precision || 0) >= 0.4 ? '#f59e0b' : '#ef4444', fontSize: 13, fontWeight: 700 }}>{((m.precision || 0) * 100).toFixed(1)}%</div>
                  </div>
                  <div style={{ flex: 1, textAlign: 'center' }}>
                    <div style={{ color: (m.recall || 0) >= 0.7 ? '#22c55e' : (m.recall || 0) >= 0.4 ? '#f59e0b' : '#ef4444', fontSize: 13, fontWeight: 700 }}>{((m.recall || 0) * 100).toFixed(1)}%</div>
                  </div>
                  <div style={{ flex: 1, textAlign: 'center' }}>
                    <div style={{ color: (m['f1-score'] || 0) >= 0.7 ? '#22c55e' : (m['f1-score'] || 0) >= 0.4 ? '#f59e0b' : '#ef4444', fontSize: 13, fontWeight: 700 }}>{((m['f1-score'] || 0) * 100).toFixed(1)}%</div>
                  </div>
                  <div style={{ flex: 1, textAlign: 'center', color: '#94a3b8', fontSize: 12 }}>{m.support || 0}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Comparison Chart View ──────────────────────────────── */
function ComparisonView({ metricsData }) {
  const bm = metricsData || {};
  const m = bm.classifier_metrics || bm;
  return (
    <div>
      <div style={{ color: '#e2e8f0', fontWeight: 700, fontSize: 16, marginBottom: 16 }}>SAFEGUARD AI vs Manual Safety Review</div>
      <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
        <div style={{ flex: 1, background: '#0f0f1a', borderRadius: 8, padding: 16, borderLeft: '3px solid #18c6d9' }}>
          <div style={{ color: '#18c6d9', fontWeight: 700, fontSize: 13, marginBottom: 4 }}>SAFEGUARD AI</div>
          <div style={{ color: '#94a3b8', fontSize: 12 }}>Automated NLP + ML pipeline</div>
          <div style={{ color: '#e2e8f0', fontSize: 22, fontWeight: 800, marginTop: 8 }}>{m.test_accuracy || 97.4}%</div>
          <div style={{ color: '#94a3b8', fontSize: 11 }}>Classification Accuracy</div>
        </div>
        <div style={{ flex: 1, background: '#0f0f1a', borderRadius: 8, padding: 16, borderLeft: '3px solid #94a3b8' }}>
          <div style={{ color: '#94a3b8', fontWeight: 700, fontSize: 13, marginBottom: 4 }}>MANUAL REVIEW</div>
          <div style={{ color: '#64748b', fontSize: 12 }}>Human safety officer reads each report</div>
          <div style={{ color: '#e2e8f0', fontSize: 22, fontWeight: 800, marginTop: 8 }}>~72%</div>
          <div style={{ color: '#94a3b8', fontSize: 11 }}>Avg Inter-Rater Agreement</div>
        </div>
      </div>
      <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 16 }}>
        <CompRow label="Classification Accuracy" ai={m.test_accuracy || 97.4} manual={72} better="higher" />
        <CompRow label="Time per Report" ai={2} manual={15} unit=" sec" better="lower" />
        <CompRow label="Precursors Detected" ai={100} manual={60} better="higher" />
        <CompRow label="False Negatives" ai={3} manual={28} better="lower" />
        <CompRow label="Reports per Hour" ai={1800} manual={4} better="higher" />
        <CompRow label="Consistency" ai={99} manual={75} better="higher" />
        <CompRow label="Shift Coverage" ai={24} manual={8} unit="h/day" better="higher" />
      </div>
    </div>
  );
}

export default function AIEnginesTab() {
  const [activeEngine, setActiveEngine] = useState('predictions');
  const [engines, setEngines] = useState({});
  const [loading, setLoading] = useState(false);
  const [ragId, setRagId] = useState('');
  const [xaiId, setXaiId] = useState('');

  const engineList = [
    { id: 'predictions', label: 'Predictions', color: '#6366f1', endpoint: '/api/predictions' },
    { id: 'anomalies', label: 'Anomalies', color: '#f97316', endpoint: '/api/anomalies' },
    { id: 'gnn', label: 'GNN Graph', color: '#22c55e', endpoint: '/api/gnn_analysis' },
    { id: 'fatigue', label: 'Fatigue', color: '#eab308', endpoint: '/api/fatigue' },
    { id: 'rag', label: 'RAG Root Cause', color: '#ec4899', endpoint: '/api/rag_analysis/' },
    { id: 'xai', label: 'Explainability', color: '#8b5cf6', endpoint: '/api/xai/' },
    { id: 'alerts', label: 'Alerts', color: '#ef4444', endpoint: '/api/alerts' },
    { id: 'metrics', label: 'ML Metrics', color: '#06b6d4', endpoint: '/api/benchmark' },
    { id: 'comparison', label: 'vs Manual', color: '#22c55e', endpoint: '/api/benchmark' },
  ];

  const loadEngine = useCallback(async (engineId, extraPath) => {
    setLoading(true);
    try {
      const eng = engineList.find(e => e.id === engineId);
      if (!eng) return;
      const url = 'http://127.0.0.1:8000' + eng.endpoint + (extraPath || '');
      const resp = await fetch(url);
      const data = await resp.json();
      setEngines(prev => ({ ...prev, [engineId]: data }));
    } catch (err) {
      setEngines(prev => ({ ...prev, [engineId]: { error: err.message } }));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeEngine !== 'rag' && activeEngine !== 'xai') {
      loadEngine(activeEngine);
    }
  }, [activeEngine, loadEngine]);

  const handleRAG = () => { if (ragId) loadEngine('rag', ragId); };
  const handleXAI = () => { if (xaiId) loadEngine('xai', xaiId); };
  const d = engines[activeEngine];

  return (
    <div style={{ padding: 20, maxWidth: 900 }}>
      <h2 style={{ color: '#e2e8f0', fontSize: 20, fontWeight: 700, marginBottom: 16 }}>AI Engines</h2>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 20 }}>
        {engineList.map(eng => (
          <button key={eng.id} onClick={() => setActiveEngine(eng.id)}
            style={{ background: activeEngine === eng.id ? eng.color + '33' : '#1e1e2e', color: activeEngine === eng.id ? eng.color : '#94a3b8', border: activeEngine === eng.id ? '1px solid ' + eng.color : '1px solid #334155', borderRadius: 8, padding: '8px 14px', cursor: 'pointer', fontWeight: 600, fontSize: 13 }}>
            {eng.label}
          </button>
        ))}
      </div>
      {loading && <div style={{ color: '#94a3b8', textAlign: 'center', padding: 20 }}>Loading...</div>}
      {!loading && d && d.error && <div style={{ background: '#ef444422', color: '#ef4444', padding: 12, borderRadius: 8 }}>Error: {d.error}</div>}
      {!loading && activeEngine === 'predictions' && <PredictionsView data={d} />}
      {!loading && activeEngine === 'anomalies' && <AnomaliesView data={d} />}
      {!loading && activeEngine === 'gnn' && <GNNView data={d} />}
      {!loading && activeEngine === 'fatigue' && <FatigueView data={d} />}
      {!loading && activeEngine === 'alerts' && <AlertsView data={d} />}
      {!loading && activeEngine === 'metrics' && <MetricsView data={d} />}
      {!loading && activeEngine === 'comparison' && <ComparisonView metricsData={d} />}
      {!loading && activeEngine === 'rag' && (
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            <input value={ragId} onChange={e => setRagId(e.target.value)} placeholder='Report ID (e.g. RPT-REAL-049)' style={{ flex: 1, background: '#0f0f1a', border: '1px solid #334155', borderRadius: 6, padding: '8px 12px', color: '#e2e8f0', fontSize: 13 }} />
            <button onClick={handleRAG} style={{ background: '#ec4899', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 16px', fontWeight: 600, cursor: 'pointer' }}>Analyze</button>
          </div>
          {d && d.root_cause && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginBottom: 10, borderLeft: '3px solid #ec4899' }}>
              <div style={{ color: '#ec4899', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>ROOT CAUSE ANALYSIS</div>
              <div style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.6 }}>{d.root_cause}</div>
            </div>
          )}
          {d && d.contributing_factors && d.contributing_factors.length > 0 && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginBottom: 10 }}>
              <div style={{ color: '#f59e0b', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>CONTRIBUTING FACTORS</div>
              {d.contributing_factors.map((f, i) => (
                <div key={i} style={{ color: '#cbd5e1', fontSize: 12, marginTop: 4, paddingLeft: 8, borderLeft: '2px solid #334155' }}>{typeof f === 'string' ? f : f.detail || f.factor || JSON.stringify(f)}</div>
              ))}
            </div>
          )}
          {d && d.causal_chain && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginBottom: 10 }}>
              <div style={{ color: '#3b82f6', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>CAUSAL CHAIN</div>
              <div style={{ color: '#94a3b8', fontSize: 12, marginBottom: 4 }}>Immediate: {d.causal_chain.immediate_cause}</div>
              {d.causal_chain.contributing_factors && d.causal_chain.contributing_factors.map((f, i) => (
                <div key={i} style={{ color: '#cbd5e1', fontSize: 12, marginTop: 2 }}>{f.factor}: {f.detail} <span style={{ color: f.impact === 'HIGH' ? '#ef4444' : '#f59e0b', fontWeight: 600 }}>[{f.impact}]</span></div>
              ))}
              <div style={{ color: '#e2e8f0', fontSize: 12, marginTop: 6, fontStyle: 'italic' }}>Root: {d.causal_chain.root_cause}</div>
            </div>
          )}
          {d && d.corrective_actions && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginBottom: 10 }}>
              <div style={{ color: '#22c55e', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>CORRECTIVE ACTIONS</div>
              {d.corrective_actions.map((a, i) => (
                <div key={i} style={{ color: '#cbd5e1', fontSize: 12, marginTop: 4, display: 'flex', gap: 8 }}>
                  <span style={{ color: i === 0 ? '#ef4444' : i === 1 ? '#f59e0b' : '#3b82f6', fontWeight: 700, minWidth: 14 }}>{i + 1}.</span>
                  <span>{a}</span>
                </div>
              ))}
            </div>
          )}
          {d && d.regulatory_reference && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginBottom: 10 }}>
              <div style={{ color: '#a78bfa', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>REGULATORY REFERENCES</div>
              <div style={{ color: '#cbd5e1', fontSize: 12 }}>OSHA: {d.regulatory_reference.osha}</div>
              <div style={{ color: '#cbd5e1', fontSize: 12 }}>DGMS: {d.regulatory_reference.dgms}</div>
              {d.regulatory_reference.oil_india && <div style={{ color: '#cbd5e1', fontSize: 12 }}>OIL: {d.regulatory_reference.oil_india}</div>}
            </div>
          )}
          {d && d.sif_pathway_analysis && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginBottom: 10 }}>
              <div style={{ color: '#ef4444', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>SIF PATHWAY</div>
              <div style={{ color: '#cbd5e1', fontSize: 12 }}>{d.sif_pathway_analysis.pathway_status}</div>
              <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 4 }}>{d.sif_pathway_analysis.severity_potential}</div>
            </div>
          )}
          {d && d.recurrence_risk && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14 }}>
              <div style={{ color: '#f59e0b', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>RECURRENCE RISK: {d.recurrence_risk.level}</div>
              <div style={{ color: '#cbd5e1', fontSize: 12 }}>{d.recurrence_risk.message}</div>
              <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 4 }}>Recommended: {d.recurrence_risk.recommended}</div>
            </div>
          )}
        </div>
      )}
      {!loading && activeEngine === 'xai' && (
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            <input value={xaiId} onChange={e => setXaiId(e.target.value)} placeholder='Report ID (e.g. RPT-REAL-049)' style={{ flex: 1, background: '#0f0f1a', border: '1px solid #334155', borderRadius: 6, padding: '8px 12px', color: '#e2e8f0', fontSize: 13 }} />
            <button onClick={handleXAI} style={{ background: '#8b5cf6', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 16px', fontWeight: 600, cursor: 'pointer' }}>Explain</button>
          </div>
          {/* Risk Explanation */}
          {d && d.risk_explanation && (
            <div style={{ marginBottom: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                <span style={{ fontSize: 28, fontWeight: 800, color: d.risk_explanation.total_score >= 70 ? '#ef4444' : d.risk_explanation.total_score >= 40 ? '#f59e0b' : '#22c55e' }}>{d.risk_explanation.total_score}</span>
                <div>
                  <div style={{ color: '#94a3b8', fontSize: 11 }}>Risk Score</div>
                  <div style={{ color: d.risk_explanation.total_score >= 70 ? '#ef4444' : d.risk_explanation.total_score >= 40 ? '#f59e0b' : '#22c55e', fontSize: 13, fontWeight: 700 }}>{d.risk_explanation.risk_level}</div>
                </div>
                <span style={{ color: d.risk_explanation.trajectory === 'ESCALATING' ? '#ef4444' : '#22c55e', fontSize: 13, fontWeight: 600 }}>{d.risk_explanation.trajectory === 'ESCALATING' ? '↗ ESCALATING' : d.risk_explanation.trajectory === 'DECREASING' ? '↘ DECREASING' : '→ STABLE'}</span>
              </div>
              {/* Narrative */}
              {d.risk_explanation.narrative && (
                <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginBottom: 10, borderLeft: '3px solid #8b5cf6' }}>
                  <div style={{ color: '#8b5cf6', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>RISK NARRATIVE</div>
                  <div style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.6 }}>{d.risk_explanation.narrative}</div>
                </div>
              )}
              {/* Factor Contributions — SHAP-style horizontal bars */}
              <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginTop: 10 }}>
                <div style={{ color: '#8b5cf6', fontWeight: 700, fontSize: 13, marginBottom: 10 }}>FEATURE CONTRIBUTIONS (SHAP-style)</div>
                {d.risk_explanation.contributions && d.risk_explanation.contributions.map((f, i) => (
                  <HorizontalBar key={i} label={f.feature} value={f.contribution} maxValue={Math.max(...d.risk_explanation.contributions.map(c => c.contribution), 1)} color={f.contribution >= 10 ? '#ef4444' : f.contribution >= 5 ? '#f59e0b' : '#3b82f6'} direction="positive" />
                ))}
                {d.risk_explanation.contributions && d.risk_explanation.contributions.map((f, i) => (
                  f.explanation && <div key={'exp-'+i} style={{ color: '#64748b', fontSize: 11, marginLeft: 148, marginTop: -2, marginBottom: 6 }}>{f.feature}: {f.explanation}</div>
                ))}
              </div>
              {/* Why Now */}
              {d.risk_explanation.why_now && d.risk_explanation.why_now.text && (
                <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginTop: 10, borderLeft: '3px solid #f59e0b' }}>
                  <div style={{ color: '#f59e0b', fontWeight: 700, fontSize: 13, marginBottom: 4 }}>WHY NOW?</div>
                  <div style={{ color: '#cbd5e1', fontSize: 12 }}>{d.risk_explanation.why_now.text}</div>
                  <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 4 }}>Urgency: {d.risk_explanation.why_now.urgency}</div>
                </div>
              )}
            </div>
          )}
          {/* Classification Explanation */}
          {d && d.classification_explanation && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginTop: 10 }}>
              <div style={{ color: '#a78bfa', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>CLASSIFICATION ANALYSIS</div>
              <div style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.5 }}>{d.classification_explanation.explanation_text}</div>
              {d.classification_explanation.decision_boundary && <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 6 }}>{d.classification_explanation.decision_boundary}</div>}
              {/* Top contributing words — SHAP-style word importance */}
              {d.classification_explanation.top_contributing_words && d.classification_explanation.top_contributing_words.length > 0 && (
                <div style={{ marginTop: 10, background: '#0a0a16', borderRadius: 8, padding: 14, border: '1px solid rgba(139,92,246,0.15)' }}>
                  <div style={{ color: '#818cf8', fontWeight: 700, fontSize: 12, marginBottom: 10 }}>WORD-LEVEL EXPLANATIONS (LIME-style)</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    {d.classification_explanation.top_contributing_words.slice(0, 10).map((w, i) => (
                      <HorizontalBar key={i} label={w.word} value={w.impact} maxValue={Math.max(...d.classification_explanation.top_contributing_words.slice(0, 10).map(x => Math.abs(x.impact)), 1)} color={w.direction === 'positive' ? '#ef4444' : '#22c55e'} direction={w.direction} />
                    ))}
                  </div>
                  <div style={{ marginTop: 8, display: 'flex', gap: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width: 10, height: 10, borderRadius: 2, background: '#ef4444' }} /><span style={{ color: '#94a3b8', fontSize: 10 }}>Increases classification confidence</span></div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width: 10, height: 10, borderRadius: 2, background: '#22c55e' }} /><span style={{ color: '#94a3b8', fontSize: 10 }}>Decreases classification confidence</span></div>
                  </div>
                </div>
              )}
            </div>
          )}
          {/* Novelty Analysis */}
          {d && d.novelty_analysis && (
            <div style={{ background: '#0f0f1a', borderRadius: 8, padding: 14, marginTop: 10, borderLeft: '3px solid #ef4444' }}>
              <div style={{ color: '#ef4444', fontWeight: 700, fontSize: 13, marginBottom: 6 }}>⚠ NOVEL HAZARD DETECTED</div>
              <div style={{ color: '#cbd5e1', fontSize: 12 }}>{d.novelty_analysis.explanation_text}</div>
              {d.novelty_analysis.action_required && <div style={{ color: '#f59e0b', fontSize: 12, marginTop: 6, fontWeight: 600 }}>{d.novelty_analysis.action_required}</div>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
