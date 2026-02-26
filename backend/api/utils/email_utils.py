import base64
import os
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def get_gmail_service():
    """
    Initializes the Gmail API service using OAuth2 Refresh Token.
    Requires: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        return None
        
    creds = Credentials(
        token=None,  # Will be populated by refresh
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.send"]
    )
    
    try:
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"Failed to initialize Gmail service: {e}")
        return None

def get_email_template(content_html, title="SARIMAX Insight"):
    """
    Master email template with 100% INLINE CSS (Gmail-compatible).
    Meralco-inspired palette: Orange header, Blue accents, Gold alerts.
    """
    dashboard_url = os.getenv("DASHBOARD_URL", "https://sarimax-thesis.vercel.app")
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0; padding:0; background-color:#f8fafc; font-family:'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f8fafc; padding:30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e2e8f0;">

    <!-- HEADER: Meralco Orange Gradient -->
    <tr>
        <td style="background: linear-gradient(135deg, #f97316 0%, #ea580c 50%, #1e40af 100%); padding:45px 30px; text-align:center;">
            <h1 style="margin:0; font-size:36px; font-weight:900; color:#ffffff; letter-spacing:-0.03em;">SARI<span style="font-weight:400; opacity:0.9;">MAX</span></h1>
            <p style="margin:10px 0 0 0; font-size:11px; font-weight:700; color:#ffffff; opacity:0.85; text-transform:uppercase; letter-spacing:0.25em;">Smart Energy Monitoring</p>
        </td>
    </tr>

    <!-- CONTENT -->
    <tr>
        <td style="padding:40px 35px; line-height:1.7; color:#334155; font-size:15px;">
            {content_html}
        </td>
    </tr>

    <!-- FOOTER: Orange top-border accent -->
    <tr>
        <td style="background-color:#f1f5f9; padding:30px 35px; text-align:center; border-top:3px solid #f97316;">
            <p style="margin:0 0 8px 0; font-weight:700; font-size:14px; color:#0f172a;">SARIMAX Energy Dashboard</p>
            <p style="margin:0 0 16px 0; font-size:12px; color:#64748b;">Designed for Efficiency &bull; Built for Savings</p>
            <a href="{dashboard_url}" style="color:#1d4ed8; text-decoration:underline; font-weight:600; font-size:13px;">Open My Dashboard</a>
        </td>
    </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

def _btn(href, label):
    """Generates a Gmail-compatible CTA button using table-based layout."""
    return f"""
    <table cellpadding="0" cellspacing="0" width="100%" style="margin:30px 0;">
    <tr><td align="center">
        <table cellpadding="0" cellspacing="0">
        <tr>
            <td style="background-color:#1d4ed8; border-radius:50px; padding:14px 35px;">
                <a href="{href}" style="color:#ffffff; text-decoration:none; font-weight:700; font-size:14px; text-transform:uppercase; letter-spacing:0.05em; display:inline-block;">{label}</a>
            </td>
        </tr>
        </table>
    </td></tr>
    </table>"""

def send_email(to_email: str, subject: str, html_body: str):
    """
    Sends an automated email using Gmail API (v1).
    """
    service = get_gmail_service()
    if not service:
        return {"status": "error", "message": "Google OAuth2 credentials missing or invalid in .env"}

    message = MIMEText(html_body, "html")
    message["to"] = to_email
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return {"status": "success", "message": f"Email sent via OAuth2 to {to_email}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_welcome_email(to_email: str):
    subject = "Welcome to SARIMAX: Your Energy Savings Start Now! ⚡"
    dashboard_url = os.getenv("DASHBOARD_URL", "https://sarimax-thesis.vercel.app")
    
    inner_html = f"""
        <h2 style="margin:0 0 20px 0; font-size:24px; font-weight:800; color:#020617; text-align:center;">Ready to power down your bill? 🏠</h2>
        <p style="margin:0 0 16px 0;">Welcome to <strong>SARIMAX</strong>. We've successfully registered your email for automated budget monitoring and energy insights.</p>
        <p style="margin:0 0 16px 0;">Our intelligent SARIMAX model is now analyzing your home's consumption patterns. You will receive <span style="color:#ea580c; font-weight:700;">real-time alerts</span> if your projected daily usage approaches your limit.</p>
        {_btn(dashboard_url, "View My Consumption")}
        <p style="font-size:13px; text-align:center; color:#94a3b8; margin:0;">Tip: Check the dashboard daily to see which appliances are contributing most to your bill.</p>
    """
    
    full_html = get_email_template(inner_html, title="Account Activated")
    return send_email(to_email, subject, full_html)

def send_threshold_alert(to_email: str, usage_percent: int, budget: float, cost: float):
    subject = f"⚠️ SARIMAX BILL ALERT: {usage_percent}% of Budget Reached"
    dashboard_url = os.getenv("DASHBOARD_URL", "https://sarimax-thesis.vercel.app")
    
    status_color = "#ea580c" if usage_percent < 100 else "#b91c1c"
    status_text = "Approaching Limit" if usage_percent < 100 else "Budget Exceeded"

    inner_html = f"""
        <div style="text-align:center; margin-bottom:25px;">
            <span style="background-color:{status_color}; color:#ffffff; padding:6px 18px; border-radius:50px; font-weight:800; font-size:11px; text-transform:uppercase; letter-spacing:0.05em;">{status_text}</span>
        </div>
        <h2 style="margin:0 0 20px 0; font-size:22px; font-weight:800; color:#020617; text-align:center;">Consumption Milestone Reached 📈</h2>
        <p style="margin:0 0 16px 0;">This is an automated advisory from your SARIMAX dashboard. Your <strong>projected total</strong> for the current period has reached <span style="color:{status_color}; font-weight:800;">{usage_percent}%</span> of your set limit.</p>
        
        <!-- Alert Box: Gold border, warm background -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#fffbeb; border:2px solid #fbbf24; border-radius:12px; margin:25px 0;">
        <tr><td style="padding:24px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="font-size:15px;">
                <tr>
                    <td style="padding-bottom:14px; color:#475569; font-weight:500;">Your Budget Goal:</td>
                    <td style="padding-bottom:14px; font-weight:800; text-align:right; color:#020617; font-size:16px;">₱{budget}</td>
                </tr>
                <tr>
                    <td colspan="2" style="border-top:1px solid #fde68a;"></td>
                </tr>
                <tr>
                    <td style="padding-top:14px; color:#475569; font-weight:500;">Projected Total:</td>
                    <td style="padding-top:14px; font-weight:800; text-align:right; color:{status_color}; font-size:22px;">₱{round(cost, 2)}</td>
                </tr>
            </table>
        </td></tr>
        </table>

        <p style="margin:0 0 16px 0; font-size:15px;">Consider auditing your high-consumption appliances like A/C units or secondary refrigerators to stay within your savings goal.</p>
        {_btn(dashboard_url, "Manage My Bill")}
    """
    
    full_html = get_email_template(inner_html, title="Urgent Action Required")
    return send_email(to_email, subject, full_html)

