# SARIMAX Energy Dashboard

A comprehensive smart energy consumption monitoring and forecasting dashboard. Built with a focus on predictive analytics using SARIMAX time series models and automated notifications via Gmail OAuth2.

## 📁 Monorepo Structure

```text
Sarimax-Thesis/
├── api/                     # Python Backend (Serverless)
│   ├── index.py             # FastAPI entry point
│   └── utils/               # Email & Notification utilities
├── src/                     # React Frontend source
├── public/                  # Frontend static assets
├── data/                    # Local energy datasets (ignored by Git)
├── package.json             # Root-level dependencies (React + Proxy)
├── requirements.txt         # Backend Python dependencies
├── vercel.json              # Vercel monorepo configuration
└── .env                     # Local credentials (ignored)
```

## 🚀 Local Development

Follow these steps to run the dashboard on your machine:

### 1. Prerequisites
- **Node.js**: [v18 or higher](https://nodejs.org/)
- **Python**: [v3.10 or higher](https://python.org/)

### 2. Frontend Setup
```bash
# Install dependencies from the root
npm install

# Start the React dashboard
npm start
```
The dashboard will open at [http://localhost:3000](http://localhost:3000).

### 3. Backend (Notifications) Setup
Wait for Step 2 to finish, then in a **second terminal**:
```bash
# Install Python libraries
pip install -r requirements.txt

# Start the FastAPI server
uvicorn api.index:app --reload
```
The API handles automated **Welcome Emails** and **Budget Alerts**.

## 📧 Gmail Notification Setup (OAuth2)

To enable email notifications, you must configure a Google Cloud project:
1.  **Google Cloud Console**: Enable the Gmail API.
2.  **OAuth Consent**: Add your email as a "Test User".
3.  **Credentials**: Create a "Desktop App" Client ID and Secret.
4.  **Refresh Token**: Run `python api/utils/generate_token.py` to generate your refresh token.
5.  **Environment Variables**: Add the following to your `.env` file:

```env
GOOGLE_CLIENT_ID="your_id"
GOOGLE_CLIENT_SECRET="your_secret"
GOOGLE_REFRESH_TOKEN="your_refresh_token"
DASHBOARD_URL="http://localhost:3000"
```

## ☁️ Deployment

This project is optimized for deployment on **Vercel**:
- **Automatic Monorepo**: Vercel detects the `api/` folder for backend functions and the root for the frontend.
- **Environment Variables**: Add your `.env` keys to the Vercel Dashboard.
- **Root Directory**: Ensure the "Root Directory" in Vercel settings is left **Empty**.

## 📄 License
MIT - Part of the TH1 SARIMAX V2 Thesis Project.
