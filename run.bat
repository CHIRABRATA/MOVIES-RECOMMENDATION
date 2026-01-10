@echo off
REM run.bat - Start both FastAPI backend and Streamlit frontend on Windows

echo.
echo ==============================================
echo  Movie Recommender Startup
echo ==============================================
echo.

echo Starting FastAPI backend on http://127.0.0.1:8000...
echo.

start cmd /k "cd /d "%~dp0" && uvicorn main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak

echo Starting Streamlit frontend on http://localhost:8501...
echo.

cd /d "%~dp0"
streamlit run app.py
