# MOVIES-RECOMMENDATION

## Quick Start

### Prerequisites
- Python 3.11+ (or use Conda)
- Dependencies installed: `pip install -r requirements.txt`
- TMDB API key in `.env` file: `TMDB_API_KEY=your_key_here`

### Running the App (Choose One)

#### Option 1: Windows Batch File (Easiest)
```bash
run.bat
```
This automatically starts both the FastAPI backend and Streamlit frontend.

#### Option 2: PowerShell Script
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser -Force
.\run.ps1 -Both
```

Or run individual components:
```powershell
# Backend only
.\run.ps1 -Backend

# Frontend only  
.\run.ps1 -Frontend
```

#### Option 3: Manual (Two Terminals)

**Terminal 1 - FastAPI Backend:**
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Streamlit Frontend:**
```bash
streamlit run app.py
```

### Accessing the App
- **Frontend (Streamlit):** http://localhost:8501
- **API Docs (FastAPI):** http://127.0.0.1:8000/docs
- **API ReDoc:** http://127.0.0.1:8000/redoc

## Architecture

- **`main.py`** - FastAPI backend (ASGI app) with movie recommendation endpoints
- **`app.py`** - Streamlit frontend UI that calls the backend API
- **`.env`** - Environment variables (API keys)