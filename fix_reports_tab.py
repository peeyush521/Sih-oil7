import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Check if Reports tab already exists
if 'REPORTS TAB' in code:
    print('Reports tab already exists')
    exit(0)

# Find the analytics tab marker
m = re.search(r'\{/\*\s*═+\s*ANALYTICS\s*TAB\s*═+\s*\*/\}', code)
if not m:
    print('ERROR: Cannot find analytics tab marker')
    exit(1)

marker = m.group(0)
print(f'Found marker at position {m.start()}')

reports_tab = '''
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
'''

# Insert before the analytics tab
code = code.replace(marker, reports_tab + '\n        ' + marker)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

print('Reports tab added successfully')
