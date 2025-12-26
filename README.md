NEW_FILE_CODE
# 🎨 Brand Intelligence API

A production-ready FastAPI backend with Streamlit frontend for brand discovery, content tracking, and intelligence signals. Easily deployable to Vercel with Supabase integration.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Deployment to Vercel](#deployment-to-vercel)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **RESTful v1 API** - Advanced filtering and pagination
- **Brand Discovery** - Multi-parameter filtering (industry, market, tier, aesthetic)
- **Intelligence Signals** - Signal feed with time-based filtering
- **Content Feed** - Platform/type filtering (Instagram, TikTok, Twitter)
- **Website Snapshots** - Creative identity and visual data tracking
- **CORS Enabled** - Frontend integration ready
- **Type-Safe** - Pydantic models for all endpoints
- **Supabase Integration** - Fully integrated database backend

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Supabase** - PostgreSQL database with real-time APIs
- **Pydantic** - Data validation

### Frontend
- **Streamlit** - Rapid UI development
- **Requests** - HTTP client
- **Pandas** - Data manipulation

### Deployment
- **Vercel** - Serverless deployment
- **Python 3.11+** - Runtime

## 📦 Prerequisites

- Python 3.11 or higher
- `uv` package manager ([install here](https://github.com/astral-sh/uv))
- Supabase account ([create here](https://supabase.com))
- GitHub account (for Vercel deployment)
- Vercel account ([create here](https://vercel.com))

## 🚀 Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/koushikfigmenta-jpg/db-mvp.git
cd db-mvp
2. Create Virtual Environment
powershell
uv venv
.venv\Scripts\Activate.ps1
3. Install Dependencies
powershell
uv sync
Or manually:
powershell
uv pip install fastapi uvicorn supabase python-dotenv streamlit requests pandas
4. Configure Environment Variables
Create a .env file in the root directory:
env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key
FRONTEND_URL=http://localhost:3000
API_URL=http://localhost:8001
Get your Supabase credentials:
Go to supabase.com
Create a new project
Go to Settings → API
Copy Project URL and Anon Public Key
5. Start the Backend (Terminal 1)
powershell
python main.py
You should see:
plaintext
INFO:     Uvicorn running on http://0.0.0.0:8001
6. Start the Frontend (Terminal 2)
powershell
streamlit run app.py
You should see:
plaintext
Local URL: http://localhost:8501
7. Test Locally
Open browser: http://localhost:8501
Go to Dashboard tab
Click "Check API Health"
Should show ✅ API Status: ok
Try creating a brand and searching for it
🌐 Deployment to Vercel
Step 1: Push to GitHub
Make sure your code is on GitHub:
powershell
git add .
git commit -m "Initial commit: FastAPI Brand Intelligence API"
git push origin main
Step 2: Create .gitignore (if not exists)
gitignore
.env
.venv/
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.streamlit/
Important: Never commit your .env file with sensitive keys!
Step 3: Deploy Backend to Vercel
Go to vercel.com
Click "New Project"
Import your GitHub repository
Select "Other" as framework
Add environment variables:
SUPABASE_URL: Your Supabase URL
SUPABASE_KEY: Your Supabase anon key
FRONTEND_URL: Your frontend domain
Click "Deploy"
Your API will be live at: https://your-project.vercel.app
Step 4: Deploy Frontend to Vercel (Optional)
You can deploy Streamlit to Vercel using Streamlit Cloud instead:
Go to streamlit.io/cloud
Click "New app"
Connect your GitHub repository
Select app.py as the main file
Add environment variable: API_URL → https://your-vercel-api.vercel.app
Deploy
Or use Streamlit's native hosting at no cost!
Step 5: Update Frontend Configuration
Once deployed, update your API URL in app.py:
python
API_BASE_URL = os.environ.get("API_URL", "https://your-vercel-api.vercel.app")
📚 API Endpoints
Health Check
plaintext
GET /health
Response:
json
{
  "status": "ok",
  "service": "Brand Intelligence API",
  "timestamp": "2025-12-26T15:30:00"
}
Brands
plaintext
POST /v1/brands
GET /v1/brands?search=Nike&industry=Sports&limit=20&offset=0
GET /v1/brands/{brand_id}?include=content,signals
Signals
plaintext
POST /v1/signals
GET /v1/signals?signal_type=launch&since=2025-01-01T00:00:00Z&limit=20
GET /v1/brands/{brand_id}/signals
Content
plaintext
POST /v1/content
GET /v1/brands/{brand_id}/content?platform=instagram&limit=20
GET /v1/content/{content_id}
GET /v1/content/{content_id}/media
Metrics
plaintext
POST /v1/content/{content_id}/metrics
GET /v1/content/{content_id}/metrics
Website Snapshots
plaintext
POST /v1/website-snapshots
GET /v1/brands/{brand_id}/snapshots
⚙️ Configuration
Environment Variables
Variable	Description	Example
SUPABASE_URL	Supabase project URL	https://xxx.supabase.co
SUPABASE_KEY	Supabase anon key	sb_xxxxx
FRONTEND_URL	Frontend domain (CORS)	http://localhost:3000
API_URL	API base URL (frontend only)	http://localhost:8001
PORT	API port (default: 8001)	8001
HOST	API host (default: 0.0.0.0)	0.0.0.0
CORS Configuration
The API allows requests from:
http://localhost:3000
http://localhost:3001
http://127.0.0.1:3000
Custom URL from FRONTEND_URL env var
To add more origins, edit apis.py:
python
allowed_origins = os.environ.get("FRONTEND_URL", "http://localhost:3000").split(",")
🐛 Troubleshooting
API won't connect (Streamlit shows error)
Check if backend is running:
powershell
curl http://localhost:8001/health
If port 8001 is in use, change it:In main.py:
python
port = int(os.environ.get("PORT", 8002))  # Change to 8002
Then update app.py:
python
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8002")
Supabase connection error
Verify credentials in .env:
powershell
echo $env:SUPABASE_URL
echo $env:SUPABASE_KEY
Test connection:
bash
curl -H "apikey: YOUR_KEY" https://your-project.supabase.co/rest/v1/brands?limit=1
Streamlit app is slow
Restart Streamlit:
powershell
# Ctrl+C to stop
streamlit run app.py --logger.level=debug
"Port already in use" error
Find and kill the process:
powershell
# On Windows, find process using port 8001
netstat -ano | findstr :8001

# Kill the process (replace PID with actual ID)
taskkill /PID <PID> /F
📁 Project Structure
plaintext
db-mvp/
├── apis.py              # FastAPI application
├── main.py              # Entry point for backend
├── app.py               # Streamlit frontend
├── wsgi.py              # WSGI compatibility layer
├── vercel.json          # Vercel deployment config
├── pyproject.toml       # Project dependencies
├── .env                 # Environment variables (git-ignored)
└── .gitignore           # Git ignore rules
🔐 Security Notes
⚠️ Never commit .env - Use Vercel's environment variables dashboard
Use SUPABASE_KEY (anon key) for public APIs only
For production, create restricted API keys in Supabase
Enable Row Level Security (RLS) in Supabase for sensitive data
📝 License
MIT License - feel free to use this project for your needs
💬 Support
For issues or questions:
Check Troubleshooting section
Review Vercel Docs
Check Supabase Docs
Check FastAPI Docs
Check Streamlit Docs
Happy building! 🚀