# run.ps1 - Start both FastAPI backend and Streamlit frontend

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Both
)

# If no flags specified, default to Both
if (-not $Backend -and -not $Frontend -and -not $Both) {
    $Both = $true
}

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Movie Recommender Startup ===" -ForegroundColor Cyan

if ($Backend -or $Both) {
    Write-Host "`nStarting FastAPI backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the backend.`n" -ForegroundColor Yellow
    
    if ($Both) {
        # Run in background if Both
        Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$ProjectDir'; uvicorn main:app --reload --host 127.0.0.1 --port 8000`"" -NoNewWindow
        Start-Sleep -Seconds 3
        Write-Host "Backend started in background. Launching frontend...`n" -ForegroundColor Green
    } else {
        # Run in foreground if Backend only
        cd $ProjectDir
        uvicorn main:app --reload --host 127.0.0.1 --port 8000
        exit
    }
}

if ($Frontend -or $Both) {
    Write-Host "Starting Streamlit frontend on http://localhost:8501 ..." -ForegroundColor Green
    cd $ProjectDir
    streamlit run app.py
}
