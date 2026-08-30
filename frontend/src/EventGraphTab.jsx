import React, { useState, useRef, useEffect } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';

// Risk level color map
const getRiskColor = (score) => {
  if (score >= 70) return '#ef4444'; // CRITICAL - red
  if (score >= 40) return '#f59e0b'; // WARNING - amber
  return '#10b981'; // NORMAL - green
};

// Edge color by relationship type
const getEdgeColor = (relation) => {
  switch (relation) {
    case 'CAUSED_BY': return '#ef4444';
    case 'INVOLVES': return '#3b82f6';
    case 'OCCURRED_AT': return '#10b981';
    default: return 'rgba(255,255,255,0.3)';
  }
};

export default function EventGraphTab({ graphElements, setCy, stateData }) {
  const [filter, setFilter] = useState('all');
  const [hoveredNode, setHoveredNode] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const cyRef = useRef(null);

  // Get unique equipment names for filter dropdown
  const equipmentList = [...new Set(
    graphElements
      .filter(e => e.data && e.data.type === 'Equipment')
      .map(e => e.data.label)
  )].sort();

  // Filter elements based on selected filter
  const filteredElements = graphElements.filter(el => {
    if (filter === 'all') return true;
    if (filter === 'critical') {
      if (el.data.source !== undefined) return true; // keep all edges
      return el.data.type !== 'Incident' || (el.data.risk_score || 0) >= 70;
    }
    if (filter === 'warnings') {
      if (el.data.source !== undefined) return true;
      return el.data.type !== 'Incident' || ((el.data.risk_score || 0) >= 40 && (el.data.risk_score || 0) < 70);
    }
    if (filter === 'precursors') {
      if (el.data.source !== undefined) return true;
      return el.data.type !== 'Incident' || el.data.is_precursor;
    }
    // For risk-level filters, also include connected nodes
    if (['critical', 'warnings', 'precursors'].includes(filter)) {
      const includedIncidents = new Set();
      const includedNodes = new Set();
      graphElements.forEach(el => {
        if (el.data.source !== undefined) return; // skip edges for now
        if (el.data.type === 'Incident') {
          const score = el.data.risk_score || 0;
          if (filter === 'critical' && score >= 70) includedIncidents.add(el.data.id);
          if (filter === 'warnings' && score >= 40 && score < 70) includedIncidents.add(el.data.id);
          if (filter === 'precursors' && el.data.is_precursor) includedIncidents.add(el.data.id);
        }
      });
      // Add connected equipment, locations, hazards
      graphElements.forEach(el => {
        if (el.data.source !== undefined) {
          if (includedIncidents.has(el.data.source)) {
            includedNodes.add(el.data.target);
          }
          if (includedIncidents.has(el.data.target)) {
            includedNodes.add(el.data.source);
          }
        }
      });
      includedIncidents.forEach(id => includedNodes.add(id));
      // Keep nodes in set + their edges
      if (el.data.source !== undefined) {
        return includedNodes.has(el.data.source) && includedNodes.has(el.data.target);
      }
      return includedNodes.has(el.data.id);
    }

    // Filter by equipment name
    if (filter.startsWith('eq:')) {
      const eqName = filter.slice(3);
      // Find all incidents connected to this equipment
      const connectedIncidents = new Set();
      graphElements.forEach(el => {
        if (el.data.source !== undefined) {
          if (el.data.source === eqName || el.data.target === eqName) {
            connectedIncidents.add(el.data.source);
            connectedIncidents.add(el.data.target);
          }
        }
      });
      connectedIncidents.add(eqName);
      if (el.data.source !== undefined) {
        return connectedIncidents.has(el.data.source) || connectedIncidents.has(el.data.target);
      }
      return connectedIncidents.has(el.data.id);
    }
    return true;
  });

  // Remove orphaned edges (edges referencing nodes not in filtered set)
  const filteredNodeIds = new Set(filteredElements.filter(e => !e.data.source).map(e => e.data.id));
  const finalElements = filteredElements.filter(el => {
    if (el.data.source !== undefined) {
      return filteredNodeIds.has(el.data.source) && filteredNodeIds.has(el.data.target);
    }
    return true;
  });

  // Build stylesheet with risk-level coloring
  const stylesheet = [
    // Base node style
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'color': '#fff',
        'text-valign': 'center',
        'text-halign': 'center',
        'text-outline-width': 2,
        'text-outline-color': '#0f172a',
        'font-size': '11px',
        'font-weight': 'bold',
        'width': 50,
        'height': 50,
        'background-color': '#3b82f6',
        'border-width': 2,
        'border-color': 'rgba(255,255,255,0.2)',
      }
    },
    // Incident nodes — colored by risk score
    {
      selector: 'node[type="Incident"][?is_precursor]',
      style: {
        'shape': 'rectangle',
        'width': 65,
        'height': 40,
        'background-color': '#ef4444',
        'border-width': 3,
        'border-color': '#fbbf24',
        'border-style': 'double',
        'font-size': '9px',
        'text-wrap': 'wrap',
        'text-max-width': '60px',
      }
    },
    {
      selector: 'node[type="Incident"][risk_score >= 70]',
      style: {
        'shape': 'rectangle',
        'width': 60,
        'height': 38,
        'background-color': '#ef4444',
        'border-width': 2,
        'border-color': '#f87171',
      }
    },
    {
      selector: 'node[type="Incident"][risk_score >= 40][risk_score < 70]',
      style: {
        'shape': 'rectangle',
        'width': 52,
        'height': 34,
        'background-color': '#f59e0b',
        'border-width': 2,
        'border-color': '#fbbf24',
      }
    },
    {
      selector: 'node[type="Incident"][risk_score < 40]',
      style: {
        'shape': 'rectangle',
        'width': 45,
        'height': 30,
        'background-color': '#10b981',
        'border-width': 1,
        'border-color': '#34d399',
      }
    },
    // Equipment nodes — larger hexagons
    {
      selector: 'node[type="Equipment"]',
      style: {
        'background-color': '#6366f1',
        'shape': 'hexagon',
        'width': 55,
        'height': 55,
        'font-size': '10px',
        'border-width': 2,
        'border-color': '#818cf8',
      }
    },
    // Location nodes — diamonds
    {
      selector: 'node[type="Location"]',
      style: {
        'background-color': '#10b981',
        'shape': 'diamond',
        'width': 45,
        'height': 45,
        'font-size': '9px',
        'border-width': 2,
        'border-color': '#34d399',
      }
    },
    // Hazard nodes — triangles
    {
      selector: 'node[type="Hazard"]',
      style: {
        'background-color': '#f59e0b',
        'shape': 'triangle',
        'width': 42,
        'height': 42,
        'font-size': '9px',
        'border-width': 2,
        'border-color': '#fbbf24',
      }
    },
    // Edge styles by relationship type
    {
      selector: 'edge[label="CAUSED_BY"]',
      style: {
        'width': 2.5,
        'line-color': '#ef4444',
        'target-arrow-color': '#ef4444',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '8px',
        'color': '#fca5a5',
        'text-rotation': 'autorotate',
        'text-margin-y': -10,
        'text-background-color': '#1e293b',
        'text-background-opacity': 0.8,
        'text-background-padding': '2px',
      }
    },
    {
      selector: 'edge[label="INVOLVES"]',
      style: {
        'width': 2,
        'line-color': '#3b82f6',
        'target-arrow-color': '#3b82f6',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '8px',
        'color': '#93c5fd',
        'text-rotation': 'autorotate',
        'text-margin-y': -10,
        'text-background-color': '#1e293b',
        'text-background-opacity': 0.8,
        'text-background-padding': '2px',
      }
    },
    {
      selector: 'edge[label="OCCURRED_AT"]',
      style: {
        'width': 1.5,
        'line-color': '#10b981',
        'target-arrow-color': '#10b981',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '8px',
        'color': '#6ee7b7',
        'text-rotation': 'autorotate',
        'text-margin-y': -10,
        'text-background-color': '#1e293b',
        'text-background-opacity': 0.8,
        'text-background-padding': '2px',
      }
    },
    // Hover effect
    {
      selector: 'node:selected',
      style: {
        'border-width': 4,
        'border-color': '#fff',
        'overlay-opacity': 0.2,
      }
    },
  ];

  const layout = {
    name: 'concentric',
    animate: true,
    animationDuration: 800,
    padding: 60,
    minNodeSpacing: 100,
    concentric: function(node) {
      // Precursors at center, then by risk score, then equipment, then locations, then hazards
      const type = node.data('type');
      const isPrecursor = node.data('is_precursor');
      const riskScore = node.data('risk_score') || 0;
      if (isPrecursor) return 10;
      if (type === 'Incident') return 8 - Math.floor(riskScore / 25);
      if (type === 'Equipment') return 5;
      if (type === 'Location') return 3;
      if (type === 'Hazard') return 2;
      return 1;
    },
    levelWidth: function() { return 2; },
    avoidOverlap: true,
    spacingFactor: 1.2,
  };

  const handleCyRef = (cy) => {
    cyRef.current = cy;
    if (setCy) setCy(cy);

    // Hover tooltip
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      const data = node.data();
      setHoveredNode(data);
      const pos = node.renderedPosition();
      setTooltipPos({ x: pos.x, y: pos.y });
    });

    cy.on('mouseout', 'node', () => {
      setHoveredNode(null);
    });
  };

  const nodeCount = finalElements.filter(e => e.data && !e.data.source).length;
  const edgeCount = finalElements.filter(e => e.data && e.data.source).length;
  const precursorCount = finalElements.filter(e => e.data && e.data.is_precursor).length;

  return (
    <div className="dashboard-grid tab-content">
      {/* Filter Controls */}
      <div className="panel surface-panel col-span-3">
        <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>🔗 Precursor Chain (Temporal Knowledge Graph)</h3>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FILTER:</span>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              style={{
                background: 'var(--bg-surface2)',
                color: 'var(--text-main)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 6,
                padding: '4px 8px',
                fontSize: '0.75rem',
                cursor: 'pointer',
              }}
            >
              <option value="all">All Nodes</option>
              <option value="critical">🔴 CRITICAL Only (70+)</option>
              <option value="warnings">🟡 Warnings Only (40-69)</option>
              <option value="precursors">⚠️ Precursors Only</option>
              <optgroup label="Equipment">
                {equipmentList.map(eq => (
                  <option key={eq} value={`eq:${eq}`}>{eq}</option>
                ))}
              </optgroup>
            </select>
          </div>
        </div>
      </div>

      {/* Graph */}
      <div className="panel surface-panel col-span-3" style={{ height: 550, position: 'relative' }}>
        <div className="panel-body" style={{ padding: 0, height: '100%', position: 'relative' }}>
          {finalElements.length > 0 ? (
            <>
              <CytoscapeComponent
                elements={finalElements}
                style={{ width: '100%', height: '100%' }}
                stylesheet={stylesheet}
                layout={layout}
                cy={handleCyRef}
              />
              {/* Hover Tooltip */}
              {hoveredNode && hoveredNode.type === 'Incident' && (
                <div style={{
                  position: 'absolute',
                  left: Math.min(tooltipPos.x + 20, 600),
                  top: Math.min(tooltipPos.y - 10, 400),
                  background: 'rgba(15, 23, 42, 0.95)',
                  border: `2px solid ${getRiskColor(hoveredNode.risk_score || 0)}`,
                  borderRadius: 8,
                  padding: '10px 14px',
                  maxWidth: 300,
                  zIndex: 100,
                  pointerEvents: 'none',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: getRiskColor(hoveredNode.risk_score || 0), marginBottom: 4 }}>
                    {hoveredNode.id}
                    {hoveredNode.is_precursor && <span style={{ marginLeft: 6, fontSize: '0.65rem', background: 'rgba(239,68,68,0.3)', padding: '1px 6px', borderRadius: 4 }}>⚠️ PRECURSOR</span>}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>
                    {hoveredNode.report_date}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-main)', lineHeight: 1.4, marginBottom: 6 }}>
                    "{hoveredNode.report_text}"
                  </div>
                  <div style={{ display: 'flex', gap: 8, fontSize: '0.65rem' }}>
                    <span style={{ color: getRiskColor(hoveredNode.risk_score || 0), fontWeight: 700 }}>
                      Risk: {hoveredNode.risk_score}/100
                    </span>
                    <span style={{ color: hoveredNode.trajectory === 'ESCALATING' ? '#ef4444' : '#10b981' }}>
                      {hoveredNode.trajectory}
                    </span>
                  </div>
                </div>
              )}
              {/* Hover for non-incident nodes */}
              {hoveredNode && hoveredNode.type !== 'Incident' && (
                <div style={{
                  position: 'absolute',
                  left: Math.min(tooltipPos.x + 20, 600),
                  top: Math.min(tooltipPos.y - 10, 400),
                  background: 'rgba(15, 23, 42, 0.95)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: 8,
                  padding: '8px 12px',
                  zIndex: 100,
                  pointerEvents: 'none',
                }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    {hoveredNode.type}: {hoveredNode.label}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 2 }}>
                    {graphElements.filter(e => e.data && e.data.source !== undefined && (e.data.source === hoveredNode.id || e.data.target === hoveredNode.id)).length} connections
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              {filter !== 'all' ? 'No nodes match this filter — try "All Nodes"' : 'No graph data yet — load some reports first'}
            </div>
          )}
        </div>
      </div>

      {/* Graph Legend */}
      <div className="panel surface-panel col-span-3">
        <div className="panel-header"><h3>Graph Legend</h3></div>
        <div className="panel-body" style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginRight: 16 }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>NODES:</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 12, height: 12, background: '#ef4444', display: 'inline-block', borderRadius: 2 }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Incident (red=CRIT)</span></span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 12, height: 12, background: '#f59e0b', display: 'inline-block', borderRadius: 2 }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Warning</span></span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 12, height: 12, background: '#10b981', display: 'inline-block', borderRadius: 2 }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Normal</span></span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 12, height: 12, background: '#6366f1', display: 'inline-block', borderRadius: '50%' }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Equipment</span></span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 12, height: 12, background: '#10b981', display: 'inline-block', transform: 'rotate(45deg)' }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Location</span></span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 0, height: 0, borderLeft: '6px solid transparent', borderRight: '6px solid transparent', borderBottom: '12px solid #f59e0b', display: 'inline-block' }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Hazard</span></span>
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>EDGES:</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 20, height: 2, background: '#ef4444', display: 'inline-block' }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>CAUSED_BY</span></span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 20, height: 2, background: '#3b82f6', display: 'inline-block' }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>INVOLVES</span></span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 20, height: 2, background: '#10b981', display: 'inline-block' }}></span><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>OCCURRED_AT</span></span>
          </div>
        </div>
      </div>

      {/* Graph Stats */}
      <div className="panel surface-panel col-span-3">
        <div className="panel-header"><h3>Graph Statistics</h3></div>
        <div className="panel-body" style={{ display: 'flex', gap: 24 }}>
          {[
            ['Total Nodes', nodeCount, 'var(--primary)'],
            ['Total Edges', edgeCount, 'var(--warning)'],
            ['Reports Loaded', stateData ? stateData.total_reports : 0, 'var(--safe)'],
            ['Precursors', precursorCount, 'var(--critical)'],
          ].map(([label, value, color]) => (
            <div key={label} style={{ flex: 1, textAlign: 'center', padding: 20, background: 'var(--bg-surface2)', borderRadius: 8 }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color }}>{value}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>{label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
