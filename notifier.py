import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Tuple

from models import Job

logger = logging.getLogger(__name__)


def notify_all(matches: List[Tuple[Job, float]], config: dict):
    """Send notifications for all matched jobs via enabled channels."""
    if not matches:
        return

    notif_config = config.get("notifications", {})

    if notif_config.get("email", {}).get("enabled"):
        _send_email(matches, notif_config["email"])

    if notif_config.get("whatsapp", {}).get("enabled"):
        _send_whatsapp(matches)


# ── Email ────────────────────────────────────────────────────────────────────

def _send_email(matches: List[Tuple[Job, float]], email_config: dict):
    """Send an email digest of matching jobs."""
    sender = os.getenv("SMTP_SENDER_EMAIL", "")
    password = os.getenv("SMTP_SENDER_PASSWORD", "")
    recipient = os.getenv("SMTP_RECIPIENT_EMAIL", "")
    smtp_server = email_config.get("smtp_server", "smtp.gmail.com")
    smtp_port = email_config.get("smtp_port", 587)

    if not all([sender, password, recipient]):
        logger.warning("Email credentials not configured in .env — skipping email notification")
        return

    subject = f"🔔 {len(matches)} New Job Match{'es' if len(matches) > 1 else ''} Found!"
    body_html = _build_email_html(matches)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        logger.info(f"Email sent to {recipient} with {len(matches)} job(s)")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


def _build_email_html(matches: List[Tuple[Job, float]]) -> str:
    rows = ""
    for job, score in matches:
        rows += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #eee;">
                <a href="{job.url}" style="color:#0073b1; text-decoration:none; font-weight:bold;">{job.title}</a>
            </td>
            <td style="padding:8px; border-bottom:1px solid #eee;">{job.company}</td>
            <td style="padding:8px; border-bottom:1px solid #eee;">{job.location}</td>
            <td style="padding:8px; border-bottom:1px solid #eee;">{score:.0f}%</td>
        </tr>"""

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #0073b1;">LinkedIn Job Matches</h2>
        <p>Found <strong>{len(matches)}</strong> new job(s) matching your criteria:</p>
        <table style="border-collapse: collapse; width: 100%;">
            <tr style="background: #0073b1; color: white;">
                <th style="padding:8px; text-align:left;">Title</th>
                <th style="padding:8px; text-align:left;">Company</th>
                <th style="padding:8px; text-align:left;">Location</th>
                <th style="padding:8px; text-align:left;">Score</th>
            </tr>
            {rows}
        </table>
        <p style="margin-top:16px; font-size:12px; color:#999;">
            Sent by LinkedIn Job Fetch Agent
        </p>
    </body>
    </html>
    """


# ── WhatsApp (Meta Cloud API — free tier) ───────────────────────────────────

def _send_whatsapp(matches: List[Tuple[Job, float]]):
    """Send WhatsApp push notification via Meta WhatsApp Cloud API.

    Free tier: 1,000 service conversations/month.
    Setup: https://developers.facebook.com → Create App → WhatsApp → API Setup
    """
    import requests

    token = os.getenv("WHATSAPP_API_TOKEN", "")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    recipient = os.getenv("WHATSAPP_RECIPIENT_PHONE", "")

    if not all([token, phone_id, recipient]):
        logger.warning("WhatsApp Cloud API credentials not configured in .env — skipping WhatsApp notification")
        return

    message_body = _build_whatsapp_message(matches)

    try:
        url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": message_body},
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            msg_id = response.json().get("messages", [{}])[0].get("id", "unknown")
            logger.info(f"WhatsApp message sent (ID: {msg_id})")
        else:
            logger.error(f"WhatsApp API returned {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")


def _build_whatsapp_message(matches: List[Tuple[Job, float]]) -> str:
    lines = [f"*{len(matches)} New Job Match{'es' if len(matches) > 1 else ''}!*\n"]
    for i, (job, score) in enumerate(matches, 1):
        lines.append(
            f"{i}. *{job.title}*\n"
            f"   Company: {job.company}\n"
            f"   Location: {job.location}\n"
            f"   Score: {score:.0f}%\n"
            f"   Link: {job.url}\n"
        )
    return "\n".join(lines)
