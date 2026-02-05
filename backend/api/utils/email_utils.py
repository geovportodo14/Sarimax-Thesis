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

def send_email(to_email: str, subject: str, html_body: str):
    """
    Sends an automated email using Gmail API (v1).
    """
    service = get_gmail_service()
    if not service:
        return {"status": "error", "message": "Google OAuth2 credentials missing or invalid in .env"}

    dashboard_url = os.getenv("DASHBOARD_URL", "https://sarimax.vercel.app")
    
    # Add dashboard link footer
    footer = f"<br><br><hr><p style='font-size:12px; color:#666;'>View your status: <a href='{dashboard_url}'>{dashboard_url}</a></p>"
    full_body = html_body + footer

    message = MIMEText(full_body, "html")
    message["to"] = to_email
    message["subject"] = subject

    # Gmail API expects base64url encoded string
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return {"status": "success", "message": f"Email sent via OAuth2 to {to_email}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_welcome_email(to_email: str):
    subject = "Welcome to Sarimax Energy Dashboard!"
    body = """
    <h2>Welcome to your Smart Energy Monitoring !</h2>
    <p>Your email has been successfully registered for automated budget alerts.</p>
    <p>Use the link below to access your real-time dashboard and start optimizing your consumption.</p>
    """
    return send_email(to_email, subject, body)

def send_threshold_alert(to_email: str, usage_percent: int, budget: float, cost: float):
    subject = f"⚠️ SARIMAX ALERT: Budget Threshold ({usage_percent}%)"
    
    status_color = "#F59E0B" if usage_percent < 100 else "#EF4444"
    status_text = "Approaching Limit" if usage_percent < 100 else "Budget Exceeded"

    body = f"""
    <h2 style="color: {status_color};">{status_text}</h2>
    <p>Your forecasted energy consumption has reached <strong>{usage_percent}%</strong> of your set budget.</p>
    <div style="background-color: #f9fafb; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb;">
        <p style="margin: 0;"><strong>Set Budget:</strong> ₱{budget}</p>
        <p style="margin: 0;"><strong>Forecasted Cost:</strong> ₱{round(cost, 2)}</p>
    </div>
    <p>Consider adjusting your appliance usage to stay within your limits.</p>
    """
    return send_email(to_email, subject, body)
