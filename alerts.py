"""
Email Alert Service — Sends notifications when SIF precursors are detected.
Uses Python's built-in smtplib. Configure SMTP settings in .env or environment.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_precursor_alert(report: dict, risk_data: dict, entities: dict):
    """
    Send an email alert when a precursor is detected.
    Returns True if sent successfully, False otherwise.
    """
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    alert_recipients = os.environ.get("ALERT_RECIPIENTS", "safety@oilindia.com")

    if not smtp_user or not smtp_pass:
        print("[alert] SMTP not configured — skipping email (set SMTP_USER and SMTP_PASS in .env)")
        return False

    try:
        score = risk_data.get("score", 0)
        trajectory = risk_data.get("trajectory", "UNKNOWN")
        sif_category = risk_data.get("sif_category", "None")
        equipment = entities.get("equipment", ["Unknown"])
        hazards = entities.get("hazards", ["Unknown"])
        locations = entities.get("locations", ["Unknown"])

        # Build HTML email
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="background: #ef4444; padding: 16px 24px; border-radius: 8px 8px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 18px;">🚨 SIF PRECURSOR ALERT — SAFEGUARD AI</h1>
                </div>
                <div style="background: #1e293b; padding: 24px; border: 1px solid #334155; border-radius: 0 0 8px 8px;">
                    <div style="margin-bottom: 16px;">
                        <span style="font-size: 48px; font-weight: bold; color: #ef4444;">{score}</span>
                        <span style="font-size: 14px; color: #94a3b8; margin-left: 8px;">/ 100 Risk Score</span>
                    </div>

                    <table style="width: 100%; margin-bottom: 16px;">
                        <tr>
                            <td style="padding: 8px 0; color: #94a3b8; border-bottom: 1px solid #334155;">Report ID</td>
                            <td style="padding: 8px 0; font-weight: bold; border-bottom: 1px solid #334155;">{report.get('id', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #94a3b8; border-bottom: 1px solid #334155;">Date</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #334155;">{report.get('date', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #94a3b8; border-bottom: 1px solid #334155;">Trajectory</td>
                            <td style="padding: 8px 0; color: #ef4444; font-weight: bold; border-bottom: 1px solid #334155;">↗ {trajectory}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #94a3b8; border-bottom: 1px solid #334155;">SIF Pathway</td>
                            <td style="padding: 8px 0; color: #f59e0b; font-weight: bold; border-bottom: 1px solid #334155;">{sif_category}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #94a3b8; border-bottom: 1px solid #334155;">Equipment</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #334155;">{', '.join(equipment)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #94a3b8; border-bottom: 1px solid #334155;">Hazards</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #334155;">{', '.join(hazards)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #94a3b8;">Location</td>
                            <td style="padding: 8px 0;">{', '.join(locations)}</td>
                        </tr>
                    </table>

                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); padding: 12px; border-radius: 6px; margin-bottom: 16px;">
                        <strong style="color: #ef4444;">Report Description:</strong><br/>
                        <span style="color: #e2e8f0;">{report.get('text', 'N/A')}</span>
                    </div>

                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 6px;">
                        <strong style="color: #f59e0b;">Risk Factors:</strong><br/>
                        {''.join(f"<div style='padding: 2px 0;'>• {k}: +{v}</div>" for k, v in risk_data.get('deltas', {}).items())}
                    </div>

                    <div style="margin-top: 20px; text-align: center;">
                        <a href="http://localhost:5173" style="background: #3b82f6; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">View in Dashboard →</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 SIF PRECURSOR ALERT — Risk Score {score} — {trajectory}"
        msg["From"] = smtp_user
        msg["To"] = alert_recipients
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, alert_recipients.split(","), msg.as_string())

        print(f"[alert] Precursor email sent to {alert_recipients} for report {report.get('id')}")
        return True

    except Exception as e:
        print(f"[alert] Failed to send email: {e}")
        return False
