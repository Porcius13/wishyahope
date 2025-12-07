# Local development startup script
Write-Host "Starting Favit application..." -ForegroundColor Green
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Set environment variables
$env:PYTHONUNBUFFERED = "1"
$env:FLASK_ENV = "development"

# Check for Firestore Service Account Key
$serviceAccountPath = Join-Path $scriptPath "miayis-service-account.json"

# Use Firestore if Service Account Key exists, otherwise use SQLite
if (-not $env:DB_BACKEND) {
    if (Test-Path $serviceAccountPath) {
        # Firestore configuration
        $env:DB_BACKEND = "firestore"
        $env:FIREBASE_CREDENTIALS_PATH = $serviceAccountPath
        $env:FIREBASE_PROJECT_ID = "miayis"
        Write-Host "✅ Firestore Service Account Key bulundu" -ForegroundColor Green
        Write-Host "Using Firestore for local development (DB_BACKEND=firestore)" -ForegroundColor Cyan
    } else {
        # SQLite fallback
        $env:DB_BACKEND = "sqlite"
        Write-Host "Using SQLite for local development (DB_BACKEND=sqlite)" -ForegroundColor Cyan
        Write-Host "To use Firestore, place miayis-service-account.json in this directory" -ForegroundColor Gray
    }
}

# Check if Python is available
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found! Please install Python." -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import flask; import flask_login; print('Dependencies OK')" 2>&1 | Out-Null
    Write-Host "Dependencies check passed" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Some dependencies may be missing. Installing..." -ForegroundColor Yellow
    Write-Host "Run: pip install -r requirements.txt" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Running: python run.py" -ForegroundColor Yellow
Write-Host "Access the application at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "If you see errors, check:" -ForegroundColor Yellow
Write-Host "  1. All dependencies are installed: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  2. Python version is 3.8 or higher" -ForegroundColor White
Write-Host "  3. Port 5000 is not in use by another application" -ForegroundColor White
Write-Host ""

# Run the application with error handling
python run.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Application failed to start!" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common solutions:" -ForegroundColor Yellow
    Write-Host "  1. Install missing packages: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "  2. Check if port 5000 is available: netstat -ano | findstr :5000" -ForegroundColor White
    Write-Host "  3. Try a different port: `$env:PORT=8080; python run.py" -ForegroundColor White
    pause
}

