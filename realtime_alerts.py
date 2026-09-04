"""Real-Time Alert System - WebSocket + browser sound + SMS-ready alert pipeline."""
import json
import asyncio
from datetime import datetime
from typing import List, Set

active_connections: Set = set()
alert_history: List[dict] = []


async def broadcast_alert(alert_data: dict):
    message = json.dumps(alert_data, default=str)
    disconnected = set()
    for ws in active_connections:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    active_connections.difference_update(disconnected)


def create_precursor_alert(report, risk_data, entities, rag_analysis=None):
    score = risk_data.get('score', 0)
    trajectory = risk_data.get('trajectory', 'STABLE')
    sif = risk_data.get('sif_category', 'None')
    equipment = entities.get('equipment', [])
    locations = entities.get('locations', [])
    hazards = entities.get('hazards', [])
    alert = {
        'type': 'PRECURSOR_ALERT',
        'timestamp': datetime.now().isoformat(),
        'severity': 'CRITICAL' if score >= 70 else 'WARNING' if score >= 40 else 'INFO',
        'report_id': report.get('id', 'Unknown'),
        'report_text': report.get('text', '')[:200],
        'risk_score': score,
        'trajectory': trajectory,
        'sif_pathway': sif,
        'equipment': equipment,
        'locations': locations,
        'hazards': hazards,
        'sound_alert': score >= 70,
        'sms_required': score >= 80,
    }
    if rag_analysis:
        alert['root_cause'] = rag_analysis.get('root_cause', '')
        alert['corrective_actions'] = rag_analysis.get('corrective_actions', [])
        alert['regulatory_reference'] = rag_analysis.get('regulatory_reference', {})
    alert_history.append(alert)
    return alert


def format_sms_message(alert):
    eq = ', '.join(alert['equipment'][:3])
    loc = ', '.join(alert['locations'][:2])
    nl = chr(10)
    parts = [
        'SAFEGUARD AI ALERT: ' + str(alert['severity']),
        'Report: ' + str(alert['report_id']),
        'Risk: ' + str(alert['risk_score']) + '/100 (' + str(alert['trajectory']) + ')',
        'SIF: ' + str(alert['sif_pathway']),
        'Equipment: ' + eq,
        'Location: ' + loc,
        'Action Required: Immediate review',
    ]
    return nl.join(parts)


def format_email_html(alert):
    color = '#ef4444' if alert['severity'] == 'CRITICAL' else '#f59e0b'
    eq = ', '.join(alert['equipment'])
    loc = ', '.join(alert['locations'])
    rc = alert.get('root_cause', '')
    actions = alert.get('corrective_actions', [])
    actions_html = ''
    if actions:
        items = ''.join('<li>' + a + '</li>' for a in actions)
        actions_html = '<p><strong>Actions:</strong></p><ul>' + items + '</ul>'
    rc_html = '<p><strong>Root Cause:</strong> ' + rc + '</p>' if rc else ''
    return ('<div style="font-family:Arial;max-width:600px;margin:0 auto;">'
        + '<div style="background:' + color + ';padding:16px;border-radius:8px 8px 0 0;">'
        + '<h2 style="color:white;margin:0;">SAFEGUARD AI - ' + alert['severity'] + ' ALERT</h2></div>'
        + '<div style="background:#1e293b;padding:24px;color:#e2e8f0;border-radius:0 0 8px 8px;">'
        + '<p><strong>Report:</strong> ' + alert['report_id'] + '</p>'
        + '<p><strong>Risk Score:</strong> ' + str(alert['risk_score']) + '/100</p>'
        + '<p><strong>Trajectory:</strong> ' + alert['trajectory'] + '</p>'
        + '<p><strong>SIF Pathway:</strong> ' + alert['sif_pathway'] + '</p>'
        + '<p><strong>Equipment:</strong> ' + eq + '</p>'
        + '<p><strong>Location:</strong> ' + loc + '</p>'
        + '<p><strong>Report:</strong> ' + alert['report_text'] + '</p>'
        + rc_html + actions_html
        + '<p><strong>Time:</strong> ' + alert['timestamp'] + '</p></div></div>')


def get_alert_history(limit=50):
    recent = alert_history[-limit:]
    return {
        'alerts': recent,
        'total': len(alert_history),
        'critical_count': sum(1 for a in alert_history if a['severity'] == 'CRITICAL'),
        'warning_count': sum(1 for a in alert_history if a['severity'] == 'WARNING'),
    }


def send_sms_alert(alert):
    message = format_sms_message(alert)
    return {
        'status': 'prepared',
        'message': message,
        'recipients': 'safety-team',
        'note': 'Integrate with Twilio/TextLocal API for actual sending',
    }
