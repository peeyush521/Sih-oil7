import React, { useState, useEffect, useCallback } from "react";
import CytoscapeComponent from "react-cytoscapejs";

// ---------- Shared color palette ----------
const COLORS = {
  bg: "#0b1220",
  panel: "#111a2e",
  panelBorder: "#1e293b",
  text: "#f1f5f9",
  muted: "#94a3b8",
  accent: "#22d3ee",
  accentDim: "rgba(34, 211, 238, 0.15)",
  critical: "#ef4444",
  warning: "#f59e0b",
  safe: "#22c55e",
};

const API = "/api";

// ---------- Small reusable panel wrapper ----------
function Panel({ title, right, children, style }) {
  return (
    <div
      style={{
        background: COLORS.panel,
        border: `1px solid ${COLORS.panelBorder}`,
        borderRadius: 12,
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        ...style,
      }}
    >
      {title && (
        <div
          style={{
            padding: "16px 20px",
            borderBottom: `1px solid ${COLORS.panelBorder}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>{title}</h3>
          {right}
        </div>
      )}
      <div style={{ padding: 20, flex: 1 }}>{children}</div>
    </div>
  );
}

function riskLevel(score) {
  if (score >= 75) return { label: "CRITICAL", color: COLORS.critical };
  if (score >= 50) return { label: "WARNING", color: COLORS.warning };
  return { label: "NORMAL", color: COLORS.safe };
}

// ---------- Risk Trajectory chart (plain SVG, fully labeled, no extra deps) ----------
function RiskTrajectoryChart({ reports }) {
  const width = 640;
  const height = 260;
  const padding = { top: 20, right: 20, bottom: 36, left: 44 };
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;

  const [hoverIdx, setHoverIdx] = useState(null);

  if (!reports.length) {
    return (
      <div style={{ color: COLORS.muted, fontStyle: "italic", textAlign: "center", padding: "40px 0" }}>
        No reports processed yet — click "Load next report" to begin.
      </div>
    );
  }

  const n = reports.length;
  const xFor = (i) => padding.left + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW);
  const yFor = (score) => padding.top + plotH - (score / 100) * plotH;
  const criticalY = yFor(75);

  const points = reports.map((r, i) => ({
    x: xFor(i),
    y: yFor(r.risk_data.score),
    score: r.risk_data.score,
    id: r.report.id,
    date: r.report.date,
  }));

  const pathD = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  return (
    <div>
      <p style={{ color: COLORS.muted, fontSize: 13, marginBottom: 8, marginTop: 0 }}>
        Each point is one processed report's computed <strong>Risk Score (0–100)</strong>, plotted in
        the order reports were loaded. The dashed red line at 75 marks the CRITICAL threshold — a
        precursor alert fires once a point crosses it.
      </p>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height: "auto" }}>
        {/* Y axis gridlines + labels */}
        {[0, 25, 50, 75, 100].map((v) => (
          <g key={v}>
            <line
              x1={padding.left}
              x2={width - padding.right}
              y1={yFor(v)}
              y2={yFor(v)}
              stroke={COLORS.panelBorder}
              strokeWidth="1"
            />
            <text x={padding.left - 10} y={yFor(v) + 4} fill={COLORS.muted} fontSize="11" textAnchor="end">
              {v}
            </text>
          </g>
        ))}
        {/* Y axis title */}
        <text
          x={-height / 2}
          y={14}
          fill={COLORS.muted}
          fontSize="11"
          textAnchor="middle"
          transform="rotate(-90)"
        >
          Risk Score (0–100)
        </text>

        {/* Critical threshold line */}
        <line
          x1={padding.left}
          x2={width - padding.right}
          y1={criticalY}
          y2={criticalY}
          stroke={COLORS.critical}
          strokeWidth="1.5"
          strokeDasharray="5,4"
        />
        <text x={width - padding.right} y={criticalY - 6} fill={COLORS.critical} fontSize="11" textAnchor="end" fontWeight="700">
          CRITICAL (75)
        </text>

        {/* Trend line */}
        <path d={pathD} fill="none" stroke={COLORS.accent} strokeWidth="2" opacity="0.6" />

        {/* Points */}
        {points.map((p, i) => (
          <g key={i} onMouseEnter={() => setHoverIdx(i)} onMouseLeave={() => setHoverIdx(null)} style={{ cursor: "pointer" }}>
            <circle
              cx={p.x}
              cy={p.y}
              r={hoverIdx === i ? 7 : 5}
              fill={p.score >= 75 ? COLORS.critical : COLORS.accent}
            />
            <text x={p.x} y={p.y - 12} fill={COLORS.text} fontSize="11" textAnchor="middle" fontWeight="600">
              {p.score}
            </text>
            <text x={p.x} y={height - padding.bottom + 16} fill={COLORS.muted} fontSize="10" textAnchor="middle">
              #{i + 1}
            </text>
          </g>
        ))}

        {/* X axis title */}
        <text x={width / 2} y={height - 4} fill={COLORS.muted} fontSize="11" textAnchor="middle">
          Report sequence (in the order loaded, oldest → newest)
        </text>
      </svg>

      {hoverIdx !== null && (
        <div
          style={{
            marginTop: 10,
            padding: 12,
            background: "rgba(0,0,0,0.25)",
            borderRadius: 8,
            fontSize: 13,
            border: `1px solid ${COLORS.panelBorder}`,
          }}
        >
          <strong>{points[hoverIdx].id}</strong> — {points[hoverIdx].date} — Risk Score{" "}
          <strong>{points[hoverIdx].score}</strong>
        </div>
      )}
    </div>
  );
}

// ---------- "Why Now?" evidence bars ----------
function WhyNowPanel({ latest }) {
  if (!latest) {
    return <div style={{ color: COLORS.muted, fontStyle: "italic" }}>No report selected yet.</div>;
  }
  const deltas = latest.risk_data.deltas || {};
  const entries = Object.entries(deltas);
  const maxVal = Math.max(1, ...entries.map(([, v]) => v));

  return (
    <div>
      <p style={{ color: COLORS.muted, fontSize: 13, marginTop: 0 }}>
        These are the individual scoring factors that were added together to produce the latest risk
        score. A bar only appears here if that factor actually contributed points.
      </p>
      {entries.length === 0 && (
        <div style={{ color: COLORS.muted, fontStyle: "italic" }}>
          No risk multipliers were triggered — this report has no detected related reports yet, so its
          score comes from severity alone.
        </div>
      )}
      {entries.map(([label, val]) => (
        <div key={label} style={{ marginBottom: 14 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
            <span>{label}</span>
            <strong style={{ color: COLORS.warning }}>+{val}</strong>
          </div>
          <div style={{ background: "rgba(255,255,255,0.08)", borderRadius: 6, height: 6 }}>
            <div
              style={{
                width: `${(val / maxVal) * 100}%`,
                height: "100%",
                background: COLORS.warning,
                borderRadius: 6,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// ---------- Overview page ----------
function OverviewPage({ reports, onLoadNext, onReset, onSimulate, loading, isComplete, simResult, simLoading }) {
  const latest = reports[reports.length - 1] || null;
  const score = latest ? latest.risk_data.score : 0;
  const level = riskLevel(score);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>Command Center</h2>
        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={onLoadNext}
            disabled={loading || isComplete}
            style={btnStyle(COLORS.accent, loading || isComplete)}
          >
            {isComplete ? "All reports loaded" : loading ? "Loading..." : "+ Load next report"}
          </button>
          <button onClick={onReset} style={btnStyle("transparent", false, true)}>
            Reset timeline
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 20 }}>
        <Panel title="Safety Risk" right={<span style={{ color: COLORS.muted, fontSize: 12 }}>Active Precursor Status</span>}>
          <div style={{ display: "flex", gap: 30, alignItems: "center" }}>
            <div>
              <div style={{ fontSize: 56, fontWeight: 800, color: level.color, lineHeight: 1 }}>{score}</div>
              <div style={{ fontSize: 18, fontWeight: 700, color: level.color, marginTop: 4 }}>{level.label}</div>
              <div style={{ color: COLORS.muted, fontSize: 13 }}>
                {latest ? latest.risk_data.trajectory : "—"}
              </div>
              {latest && latest.report.intervention_status && (
                <div style={{ marginTop: 8 }}>
                  <InterventionTag status={latest.report.intervention_status} />
                </div>
              )}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ color: COLORS.muted, fontSize: 12, marginBottom: 4 }}>Primary Target</div>
              <div style={{ fontWeight: 700, marginBottom: 12 }}>
                {latest && latest.extracted_entities.locations.length > 0
                  ? latest.extracted_entities.locations.join(", ")
                  : "No dominant location yet — needs a repeated pattern"}
              </div>
              <div style={{ color: COLORS.muted, fontSize: 12, marginBottom: 4 }}>Recommended Action</div>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
                {(latest ? latest.interventions : ["Load a report to see recommendations."]).map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>
          </div>
        </Panel>

        <Panel title="System Intelligence">
          <Row label="Reports analyzed" value={reports.length} />
          <Row label="Active precursors" value={reports.filter((r) => r.is_precursor).length} />
          <Row
            label="Open actions"
            value={reports.filter((r) => r.report.action_status === "Open").length}
          />
          <div style={{ display: "flex", gap: 8, marginTop: 16, flexWrap: "wrap" }}>
            <button
              style={{ ...btnStyle(COLORS.warning, !latest || simLoading), flex: "1 1 auto" }}
              disabled={!latest || simLoading}
              onClick={() => onSimulate("delay")}
            >
              Delay action
            </button>
            <button
              style={{ ...btnStyle(COLORS.accent, !latest || simLoading), flex: "1 1 auto" }}
              disabled={!latest || simLoading}
              onClick={() => onSimulate("in_progress")}
            >
              In progress
            </button>
            <button
              style={{ ...btnStyle(COLORS.safe, !latest || simLoading), flex: "1 1 auto" }}
              disabled={!latest || simLoading}
              onClick={() => onSimulate("resolve_action")}
            >
              ✓ Mark complete
            </button>
          </div>

          {simLoading && (
            <div style={{ marginTop: 14, color: COLORS.muted, fontSize: 13, fontStyle: "italic" }}>
              Running simulation...
            </div>
          )}

          {simResult && !simLoading && (
            <div
              style={{
                marginTop: 14,
                padding: 14,
                borderRadius: 8,
                background: "rgba(0,0,0,0.25)",
                border: `1px solid ${COLORS.panelBorder}`,
              }}
            >
              <div style={{ fontSize: 12, color: COLORS.muted, marginBottom: 8 }}>
                Applied: "{simResult.label}" — this report's status and score have been updated and
                saved. Check the Reports or Precursors tab to see it reflected there too.
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 22, fontWeight: 800, color: COLORS.muted }}>
                  {simResult.previousScore}
                </span>
                <span style={{ color: COLORS.muted }}>→</span>
                <span
                  style={{
                    fontSize: 22,
                    fontWeight: 800,
                    color: riskLevel(simResult.newScore).color,
                  }}
                >
                  {simResult.newScore}
                </span>
                <span
                  style={{
                    marginLeft: "auto",
                    fontSize: 12,
                    fontWeight: 700,
                    color: riskLevel(simResult.newScore).color,
                  }}
                >
                  {simResult.trajectory}
                </span>
              </div>
            </div>
          )}
        </Panel>
      </div>

      <Panel title="Risk Trajectory">
        <RiskTrajectoryChart reports={reports} />
      </Panel>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 20 }}>
        <Panel title="Latest Processed Signal">
          {latest ? (
            <div>
              <div style={{ fontWeight: 600, marginBottom: 8 }}>{latest.report.text}</div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {latest.extracted_entities.hazards.map((h) => (
                  <Tag key={h} text={h} color={COLORS.warning} />
                ))}
                {latest.extracted_entities.locations.map((l) => (
                  <Tag key={l} text={l} color={COLORS.safe} />
                ))}
              </div>
            </div>
          ) : (
            <div style={{ color: COLORS.muted, fontStyle: "italic" }}>Waiting for report ingestion...</div>
          )}
        </Panel>
        <Panel title="AI Reasoning">
          {latest ? (
            <div style={{ fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{latest.llm_explanation}</div>
          ) : (
            <div style={{ color: COLORS.muted, fontStyle: "italic" }}>Waiting for AI...</div>
          )}
        </Panel>
      </div>

      <Panel title="Why Now?">
        <WhyNowPanel latest={latest} />
      </Panel>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: `1px solid ${COLORS.panelBorder}` }}>
      <span style={{ color: COLORS.muted }}>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Tag({ text, color }) {
  return (
    <span
      style={{
        fontSize: 12,
        padding: "3px 10px",
        borderRadius: 12,
        background: `${color}22`,
        border: `1px solid ${color}55`,
        color,
      }}
    >
      {text}
    </span>
  );
}

const INTERVENTION_STYLE = {
  Delayed: { color: COLORS.warning, icon: "⏳" },
  "In Progress": { color: COLORS.accent, icon: "🔧" },
  Completed: { color: COLORS.safe, icon: "✓" },
};

function InterventionTag({ status }) {
  const style = INTERVENTION_STYLE[status] || { color: COLORS.muted, icon: "" };
  return <Tag text={`${style.icon} ${status}`} color={style.color} />;
}

function btnStyle(bg, disabled, outline) {
  return {
    padding: "10px 16px",
    borderRadius: 8,
    border: outline ? `1px solid ${COLORS.panelBorder}` : "none",
    background: outline ? "transparent" : bg,
    color: outline ? COLORS.muted : "#04121a",
    fontWeight: 700,
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.5 : 1,
  };
}

// ---------- Reports page ----------
function ReportsPage({ reports }) {
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Reports ({reports.length})</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {reports.length === 0 && (
          <div style={{ color: COLORS.muted, fontStyle: "italic" }}>No reports loaded yet.</div>
        )}
        {reports.slice().reverse().map((r) => {
          const level = riskLevel(r.risk_data.score);
          return (
            <Panel
              key={r.report.id}
              title={`${r.report.id} — ${r.report.date}`}
              right={
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  {r.report.intervention_status && <InterventionTag status={r.report.intervention_status} />}
                  <Tag text={level.label} color={level.color} />
                </div>
              }
            >
              <div style={{ marginBottom: 10 }}>{r.report.text}</div>
              <div style={{ fontSize: 13, color: COLORS.muted }}>
                Location: {r.report.location} · Class: {r.report_class} · Risk score: {r.risk_data.score}
              </div>
            </Panel>
          );
        })}
      </div>
    </div>
  );
}

// ---------- Precursors page ----------
function PrecursorsPage({ reports }) {
  const precursors = reports.filter((r) => r.is_precursor);
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Active Precursors ({precursors.length})</h2>
      <p style={{ color: COLORS.muted, marginTop: -8 }}>
        Reports that crossed the CRITICAL risk threshold (score ≥ 75), meaning the system detected an
        escalating pattern rather than an isolated event.
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {precursors.length === 0 && (
          <div style={{ color: COLORS.muted, fontStyle: "italic" }}>
            No precursor patterns detected yet. Keep loading reports — precursors typically emerge once
            2-3 reports at the same location/equipment build up.
          </div>
        )}
        {precursors.map((r) => (
          <Panel
            key={r.report.id}
            title={`${r.report.id} — Score ${r.risk_data.score}`}
            right={
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                {r.report.intervention_status && <InterventionTag status={r.report.intervention_status} />}
                <Tag text={r.risk_data.sif_category} color={COLORS.critical} />
              </div>
            }
          >
            <div style={{ marginBottom: 12 }}>{r.report.text}</div>
            <div style={{ fontSize: 13, color: COLORS.muted, marginBottom: 8 }}>Evidence:</div>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
              {r.risk_data.evidence.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
            <div style={{ fontSize: 13, color: COLORS.muted, marginTop: 12, marginBottom: 8 }}>
              Recommended interventions:
            </div>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, color: "#fca5a5" }}>
              {r.interventions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </Panel>
        ))}
      </div>
    </div>
  );
}

// ---------- Event Graph page ----------
const NODE_COLORS = {
  Incident: "#ef4444",
  Equipment: "#3b82f6",
  Location: "#22c55e",
  Hazard: "#f97316",
};

function EventGraphPage() {
  const [elements, setElements] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchGraph = useCallback(() => {
    setLoading(true);
    fetch(`${API}/graph_data`)
      .then((r) => r.json())
      .then((data) => {
        setElements(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  const stylesheet = [
    {
      selector: "node",
      style: {
        label: "data(label)",
        color: "#f1f5f9",
        "font-size": 10,
        "text-valign": "bottom",
        "text-margin-y": 6,
        "background-color": (ele) => NODE_COLORS[ele.data("type")] || "#64748b",
        width: 28,
        height: 28,
      },
    },
    {
      selector: "edge",
      style: {
        label: "data(label)",
        "font-size": 8,
        color: "#94a3b8",
        width: 1.5,
        "line-color": "#334155",
        "target-arrow-color": "#334155",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
      },
    },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Event Graph</h2>
        <button style={btnStyle(COLORS.accent, false)} onClick={fetchGraph}>
          Refresh
        </button>
      </div>
      <p style={{ color: COLORS.muted, marginTop: 0 }}>
        Full knowledge graph across every report processed so far. Red = report, blue = equipment, green
        = location, orange = hazard. Drag nodes to rearrange.
      </p>
      <div style={{ display: "flex", gap: 16, marginBottom: 12, fontSize: 12 }}>
        {Object.entries(NODE_COLORS).map(([label, color]) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 10, height: 10, borderRadius: "50%", background: color, display: "inline-block" }} />
            {label}
          </div>
        ))}
      </div>
      <Panel style={{ height: 600, padding: 0 }}>
        {loading ? (
          <div style={{ color: COLORS.muted, textAlign: "center", padding: 40 }}>Loading graph...</div>
        ) : elements.length === 0 ? (
          <div style={{ color: COLORS.muted, textAlign: "center", padding: 40, fontStyle: "italic" }}>
            No graph data yet — load some reports on the Overview page first.
          </div>
        ) : (
          <CytoscapeComponent
            elements={elements}
            stylesheet={stylesheet}
            style={{ width: "100%", height: 600 }}
            layout={{ name: "cose", animate: false, padding: 40 }}
          />
        )}
      </Panel>
    </div>
  );
}

// ---------- App shell / navigation ----------
const TABS = [
  { id: "overview", label: "Overview", icon: "◇" },
  { id: "reports", label: "Reports", icon: "☰" },
  { id: "precursors", label: "Precursors", icon: "⚠" },
  { id: "graph", label: "Event Graph", icon: "◇" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  const refreshState = useCallback(() => {
    fetch(`${API}/state`)
      .then((r) => r.json())
      .then((data) => {
        setReports(data.reports || []);
        setIsComplete(!!data.is_complete);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    refreshState();
  }, [refreshState]);

  const handleLoadNext = () => {
    setLoading(true);
    setSimResult(null);
    fetch(`${API}/process_next`, { method: "POST" })
      .then((r) => {
        if (!r.ok) throw new Error("No more reports");
        return r.json();
      })
      .then(() => refreshState())
      .catch(() => setIsComplete(true))
      .finally(() => setLoading(false));
  };

  const handleReset = () => {
    fetch(`${API}/reset`).then(() => {
      setReports([]);
      setIsComplete(false);
      setSimResult(null);
    });
  };

  const handleSimulate = (interventionType) => {
    const latest = reports[reports.length - 1];
    if (!latest) return;

    const labels = {
      delay: "Delayed",
      in_progress: "In Progress",
      resolve_action: "Completed",
    };
    const statusLabel = labels[interventionType] || interventionType;
    const previousScore = latest.risk_data.score;

    setSimLoading(true);
    setSimResult(null);

    // Step 1: ask the backend what score/trajectory this intervention would produce
    fetch(`${API}/simulate?intervention_type=${interventionType}`, { method: "POST" })
      .then((r) => r.json())
      .then((simData) =>
        // Step 2: persist that outcome onto the actual report so it shows up
        // everywhere (Reports, Precursors, sidebar counters) instead of only
        // flashing a one-off preview.
        fetch(`${API}/update_status`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            report_id: latest.report.id,
            status_label: statusLabel,
            new_score: simData.risk_score,
            new_trajectory: simData.trajectory,
          }),
        }).then((r) => r.json())
      )
      .then((updatedReport) => {
        setReports((prev) =>
          prev.map((r) => (r.report.id === updatedReport.report.id ? updatedReport : r))
        );
        setSimResult({
          label: statusLabel,
          previousScore,
          newScore: updatedReport.risk_data.score,
          trajectory: updatedReport.risk_data.trajectory,
        });
      })
      .catch(() => setSimResult(null))
      .finally(() => setSimLoading(false));
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: COLORS.bg, color: COLORS.text, fontFamily: "Inter, sans-serif" }}>
      {/* Sidebar */}
      <aside
        style={{
          width: 260,
          borderRight: `1px solid ${COLORS.panelBorder}`,
          padding: 24,
          display: "flex",
          flexDirection: "column",
          position: "sticky",
          top: 0,
          height: "100vh",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <span style={{ fontSize: 22 }}>🛡️</span>
          <strong style={{ fontSize: 18, letterSpacing: 0.5 }}>SAFEGUARD AI</strong>
        </div>
        <div style={{ color: COLORS.muted, fontSize: 13, marginBottom: 32 }}>Industrial Safety Intelligence</div>

        <nav style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1 }}>
          {TABS.map((tab) => {
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  textAlign: "left",
                  padding: "12px 14px",
                  borderRadius: 8,
                  border: active ? `1px solid ${COLORS.accent}` : "1px solid transparent",
                  background: active ? COLORS.accentDim : "transparent",
                  color: active ? COLORS.accent : COLORS.muted,
                  fontWeight: 600,
                  cursor: "pointer",
                  fontSize: 14,
                }}
              >
                <span>{tab.icon}</span>
                {tab.label}
                {tab.id === "precursors" && reports.filter((r) => r.is_precursor).length > 0 && (
                  <span
                    style={{
                      marginLeft: "auto",
                      background: COLORS.critical,
                      color: "white",
                      borderRadius: 10,
                      fontSize: 11,
                      padding: "1px 7px",
                    }}
                  >
                    {reports.filter((r) => r.is_precursor).length}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        <button onClick={handleLoadNext} disabled={loading || isComplete} style={{ ...btnStyle(COLORS.accent, loading || isComplete), marginTop: 20 }}>
          {isComplete ? "All reports loaded" : loading ? "Loading..." : "+ Load next report"}
        </button>
        <button onClick={handleReset} style={{ ...btnStyle("transparent", false, true), marginTop: 10 }}>
          Reset timeline
        </button>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, padding: 32, overflowY: "auto" }}>
        {activeTab === "overview" && (
          <OverviewPage
            reports={reports}
            onLoadNext={handleLoadNext}
            onReset={handleReset}
            onSimulate={handleSimulate}
            loading={loading}
            isComplete={isComplete}
            simResult={simResult}
            simLoading={simLoading}
          />
        )}
        {activeTab === "reports" && <ReportsPage reports={reports} />}
        {activeTab === "precursors" && <PrecursorsPage reports={reports} />}
        {activeTab === "graph" && <EventGraphPage />}
      </main>
    </div>
  );
}