import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

# Scopes needed for sending email
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def generate_refresh_token():
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip('"').strip("'").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip('"').strip("'").strip()

    if not client_id or not client_secret:
        print("❌ Error: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not found in .env")
        return

    print(f"DEBUG: Using Client ID: {client_id[:15]}...")
    print(f"DEBUG: Using Client Secret: {client_secret[:5]}...")

    # We try both "installed" and "web" configurations
    client_configs = [
        {"installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }},
        {"web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }}
    ]

    for i, config in enumerate(client_configs):
        type_label = "installed" if "installed" in config else "web"
        print(f"\nAttempting with '{type_label}' configuration (Attempt {i+1}/2)...")
        
        try:
            flow = InstalledAppFlow.from_client_config(config, SCOPES)
            print("\n--- GOOGLE AUTHENTICATION ---")
            print("1. A browser window will open, or a link will be shown below.")
            print("2. Log in with your Gmail account and allow the permissions.")
            
            creds = flow.run_local_server(port=0, success_message="Authorization successful! You can close this tab.")
            
            print("\n✅ New Refresh Token obtained!")
            print("-" * 40)
            print(creds.refresh_token)
            print("-" * 40)
            print("\nCopy the token above and paste it into your .env file as GOOGLE_REFRESH_TOKEN.")
            return # Exit if successful
            
        except Exception as e:
            print(f"❌ Error with '{type_label}': {e}")
            if "invalid_client" in str(e):
                print("Tip: This usually means the Client ID or Secret is incorrect.")
            elif i == 0:
                print("Trying fallback configuration...")
    
    print("\n❌ Failed to obtain refresh token with both configurations.")

if __name__ == "__main__":
    generate_refresh_token()
