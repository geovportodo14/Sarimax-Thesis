from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Scopes required for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def generate_refresh_token():
    print("--- Sarimax Gmail Token Generator ---")
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()

    config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(config, SCOPES)
    # This will open your default browser for authentication
    creds = flow.run_local_server(port=0)

    print("\n--- SUCCESS! ---")
    print("Copy this Refresh Token into your .env file:")
    print(f"GOOGLE_REFRESH_TOKEN=\"{creds.refresh_token}\"")
    print("\nAlso add these:")
    print(f"GOOGLE_CLIENT_ID=\"{client_id}\"")
    print(f"GOOGLE_CLIENT_SECRET=\"{client_secret}\"")
    print("----------------")

if __name__ == "__main__":
    generate_refresh_token()
