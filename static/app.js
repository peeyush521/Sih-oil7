document.addEventListener('DOMContentLoaded', () => {
    const processNextBtn = document.getElementById('process-next-btn');
    const resetBtn = document.getElementById('reset-btn');
    const submitCustomBtn = document.getElementById('submit-custom-btn');
    const customTextarea = document.getElementById('custom-report-text');
    const simBtns = document.querySelectorAll('.sim-btn');
    
    let currentState = null;

    const elTotal = document.getElementById('stat-total');
    const elPrecursors = document.getElementById('stat-precursors');
    const elLatestReport = document.getElementById('latest-report-container');
    const elRiskAssessment = document.getElementById('risk-assessment-container');
    const elLlmExplanation = document.getElementById('llm-explanation-container');
    const elTimeline = document.getElementById('incident-timeline');
    const elSimResults = document.getElementById('sim-results');
    const elAlertContainer = document.getElementById('alert-container');
    
    let cy = null;
    let isComplete = false;

    async function processNext() {
        processNextBtn.disabled = true;
        processNextBtn.innerText = "Processing...";
        
        try {
            const res = await fetch('/api/process_next', { method: 'POST' });
            if (!res.ok) {
                if(res.status === 400) {
                    processNextBtn.innerText = "Simulation Complete";
                    isComplete = true;
                } else {
                    throw new Error("Failed to process");
                }
                return;
            }
            const data = await res.json();
            currentState = data;
            
            await updateDashboard();
            await renderGraph();
            updateSimResults("Select an intervention to see predicted risk trajectory.");
            
        } catch(e) {
            console.error(e);
        } finally {
            if(!isComplete) {
                processNextBtn.disabled = false;
                processNextBtn.innerText = "Process Next Report";
            }
        }
    }

    async function submitCustomReport() {
        const text = customTextarea.value.trim();
        if(!text) return;
        
        submitCustomBtn.disabled = true;
        submitCustomBtn.innerText = "Analyzing...";
        
        try {
            const res = await fetch('/api/submit_report', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            
            if (!res.ok) throw new Error("Failed to process");
            
            const data = await res.json();
            currentState = data;
            
            customTextarea.value = '';
            await updateDashboard();
            await renderGraph();
            updateSimResults("Select an intervention to see predicted risk trajectory.");
            
        } catch(e) {
            console.error(e);
        } finally {
            submitCustomBtn.disabled = false;
            submitCustomBtn.innerText = "Analyze Custom Report";
        }
    }

    async function resetSimulation() {
        await fetch('/api/reset');
        isComplete = false;
        currentState = null;
        processNextBtn.disabled = false;
        processNextBtn.innerText = "Process Next Report";
        
        elTotal.innerText = '0';
        elPrecursors.innerText = '0';
        document.getElementById('stat-unresolved').innerText = '0';
        
        elLatestReport.innerHTML = '<div class="empty-state">Waiting for next report...</div>';
        elRiskAssessment.innerHTML = '<div class="empty-state">No risk data available</div>';
        elLlmExplanation.innerHTML = '<div class="empty-state">Waiting for AI...</div>';
        elTimeline.innerHTML = '<div class="empty-state">Timeline empty</div>';
        elSimResults.innerHTML = 'Select an intervention to see predicted risk trajectory.';
        elAlertContainer.innerHTML = '';
        
        if (cy) {
            cy.elements().remove();
        }
        
        loadState();
    }
    
    function updateSimResults(htmlText) {
        elSimResults.innerHTML = htmlText;
    }

    async function simulateIntervention(action) {
        if(!currentState) return;
        
        try {
            const res = await fetch(`/api/simulate?intervention_type=${action}`, { method: 'POST' });
            const data = await res.json();
            
            let html = `
                <div style="display: flex; align-items: center; justify-content: center;">
                    <span class="sim-result-score">${data.risk_score}</span>
                    <span class="risk-trend ${data.trajectory.toLowerCase()}">${data.trajectory === 'ESCALATING' ? '↗' : (data.trajectory === 'DECREASING' ? '↘' : '→')} ${data.trajectory}</span>
                </div>
            `;
            updateSimResults(html);
            
        } catch(e) {
            console.error(e);
        }
    }

    async function updateDashboard() {
        const res = await fetch('/api/state');
        const stateData = await res.json();
        
        elTotal.innerText = stateData.total_reports;
        
        let precursors = 0;
        let unresolved = 0;
        
        stateData.reports.forEach(r => {
            if(r.is_precursor) precursors++;
            if(r.report.action_status === "Open") unresolved++;
        });
        
        elPrecursors.innerText = precursors;
        document.getElementById('stat-unresolved').innerText = unresolved;
        
        if(currentState) {
            const r = currentState.report;
            const ent = currentState.extracted_entities;
            
            let tagsHtml = `<span class="tag" style="background: rgba(255,255,255,0.2); border-color: #fff; color: #fff;">🏷️ ${currentState.report_class}</span>`;
            ent.equipment.forEach(e => tagsHtml += `<span class="tag equipment">⚙️ ${e}</span>`);
            ent.hazards.forEach(h => tagsHtml += `<span class="tag hazard">⚠️ ${h}</span>`);
            ent.locations.forEach(l => tagsHtml += `<span class="tag location">📍 ${l}</span>`);
            
            elLatestReport.innerHTML = `
                <div class="report-content">${r.text}</div>
                <div class="entities-tags">${tagsHtml}</div>
            `;
            
            // LLM Explanation formatting
            let llmHtml = currentState.llm_explanation.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
            elLlmExplanation.innerHTML = `<div style="padding: 10px; background: rgba(59, 130, 246, 0.1); border-left: 3px solid var(--accent); border-radius: 4px;">${llmHtml}</div>`;
            
            const risk = currentState.risk_data;
            let riskClass = 'safe';
            if(risk.score >= 70) riskClass = 'critical';
            else if(risk.score >= 40) riskClass = 'warning';
            
            let evidenceHtml = '';
            risk.evidence.forEach(e => evidenceHtml += `<li>${e}</li>`);
            
            let recommendationsHtml = '';
            currentState.interventions.forEach(i => recommendationsHtml += `<li>${i}</li>`);
            
            const sifBadge = document.getElementById('sif-category-badge');
            if(risk.sif_category && risk.sif_category !== "None") {
                sifBadge.style.display = "block";
                sifBadge.innerText = `SIF Pathway: ${risk.sif_category}`;
            } else {
                sifBadge.style.display = "none";
            }
            
            let deltasHtml = '';
            if(risk.deltas) {
                for (const [key, val] of Object.entries(risk.deltas)) {
                    deltasHtml += `<div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>${key}</span> <span style="color: #ff6b6b; font-weight: bold;">+${val}</span></div>`;
                }
            }
            
            elRiskAssessment.innerHTML = `
                <div style="flex: 1;">
                    <div class="risk-score-container">
                        <div class="risk-circle ${riskClass}">${risk.score}</div>
                        <div>
                            <div style="font-size: 0.9rem; color: var(--text-muted)">Risk Trajectory</div>
                            <div class="risk-trend ${risk.trajectory.toLowerCase()}">${risk.trajectory === 'ESCALATING' ? '↗' : (risk.trajectory === 'DECREASING' ? '↘' : '→')} ${risk.trajectory}</div>
                        </div>
                    </div>
                    
                    <h4 style="color: var(--text-muted); margin-bottom: 8px;">Evidence</h4>
                    <ul class="evidence-list">
                        ${evidenceHtml || '<li>No specific precursor evidence</li>'}
                    </ul>
                    
                    ${risk.score >= 70 ? `
                    <div class="recommendations-box">
                        <h4>Recommended Interventions</h4>
                        <ul>
                            ${recommendationsHtml}
                        </ul>
                    </div>
                    ` : ''}
                </div>
                <div style="flex: 1; padding-left: 20px; border-left: 1px solid var(--border);">
                    <h4 style="color: var(--text-muted); margin-bottom: 12px;">Why did risk change?</h4>
                    <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 12px; font-size: 0.9rem;">
                        ${deltasHtml || '<div>No significant compounding factors.</div>'}
                        <div style="border-top: 1px solid var(--border); margin-top: 8px; padding-top: 8px; display: flex; justify-content: space-between; font-weight: bold;">
                            <span>Total Compounding Score</span>
                            <span style="color: #ff6b6b;">+${Object.values(risk.deltas || {}).reduce((a,b)=>a+b, 0)}</span>
                        </div>
                    </div>
                </div>
            `;
            
            if(currentState.is_precursor) {
                elAlertContainer.innerHTML = `
                    <div class="alert-banner">
                        <div class="alert-icon">🚨</div>
                        <div class="alert-content">
                            <h3>PRECURSOR DETECTED</h3>
                            <p>High risk pattern emerging related to ${ent.equipment.length > 0 ? ent.equipment[0].toUpperCase() : 'recent events'}. Immediate intervention recommended.</p>
                        </div>
                    </div>
                `;
            } else {
                elAlertContainer.innerHTML = '';
            }
        }
        
        let timelineHtml = '';
        stateData.reports.forEach(r => {
            const dateStr = new Date(r.report.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const isP = r.is_precursor ? 'precursor' : '';
            timelineHtml += `
                <div class="timeline-item ${isP}">
                    <div class="timeline-date">${dateStr} - ${r.report.id}</div>
                    <div class="timeline-content">${r.report.text}</div>
                </div>
            `;
        });
        
        elTimeline.innerHTML = timelineHtml || '<div class="empty-state">Timeline empty</div>';
    }

    async function renderGraph() {
        try {
            const res = await fetch('/api/graph_data');
            const elements = await res.json();
            
            if (!cy) {
                cy = cytoscape({
                    container: document.getElementById('cy'),
                    elements: elements,
                    style: [
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
                        {
                            selector: 'node[type="Incident"]',
                            style: { 'background-color': '#ef4444', 'shape': 'rectangle' }
                        },
                        {
                            selector: 'node[type="Equipment"]',
                            style: { 'background-color': '#3b82f6', 'shape': 'hexagon' }
                        },
                        {
                            selector: 'node[type="Location"]',
                            style: { 'background-color': '#10b981', 'shape': 'diamond' }
                        },
                        {
                            selector: 'node[type="Hazard"]',
                            style: { 'background-color': '#f59e0b', 'shape': 'triangle' }
                        },
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
                    ],
                    layout: {
                        name: 'cose',
                        animate: true,
                        padding: 30
                    }
                });
            } else {
                cy.elements().remove();
                cy.add(elements);
                cy.layout({ name: 'cose', animate: true }).run();
            }
        } catch(e) {
            console.error("Failed to render graph", e);
        }
    }

    async function loadState() {
        try {
            const res = await fetch('/api/state');
            const stateData = await res.json();
            
            if (stateData.reports.length > 0) {
                currentState = stateData.reports[stateData.reports.length - 1];
                updateDashboard();
                renderGraph();
            }
        } catch(e) {
            console.error("Failed to load initial state", e);
        }
    }

    processNextBtn.addEventListener('click', processNext);
    resetBtn.addEventListener('click', resetSimulation);
    submitCustomBtn.addEventListener('click', submitCustomReport);
    
    simBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const action = e.target.getAttribute('data-action');
            simulateIntervention(action);
        });
    });

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            const text = item.innerText;
            if(text === 'Risk Investigation') {
                const el = document.getElementById('risk-assessment-container');
                if (el) el.scrollIntoView({behavior: 'smooth', block: 'center'});
            } else if (text === 'Timeline') {
                const el = document.getElementById('incident-timeline');
                if (el) el.scrollIntoView({behavior: 'smooth', block: 'center'});
            } else {
                window.scrollTo({top: 0, behavior: 'smooth'});
            }
        });
    });

    loadState();
});
