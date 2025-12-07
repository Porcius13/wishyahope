# Local Development Setup

## Quick Start (SQLite - No Firebase Required)

For local development without Firebase credentials, use SQLite:

### Option 1: Use the PowerShell Script (Recommended)
```powershell
.\start_local.ps1
```

This script automatically sets `DB_BACKEND=sqlite` for local development.

### Option 2: Set Environment Variable Manually
```powershell
$env:DB_BACKEND = "sqlite"
python run.py
```

Or in Command Prompt:
```cmd
set DB_BACKEND=sqlite
python run.py
```

### Option 3: Create a .env file
Create a `.env` file in the project root:
```
DB_BACKEND=sqlite
```

## Using Firestore (Requires Firebase Setup)

If you want to use Firestore for local development, you need to set up Firebase credentials:

### Option 1: Service Account Key File
1. Download your Firebase service account key from Firebase Console
2. Set the path:
   ```powershell
   $env:FIREBASE_CREDENTIALS_PATH = "C:\path\to\service-account-key.json"
   $env:DB_BACKEND = "firestore"
   ```

### Option 2: Environment Variable (JSON String)
```powershell
$env:FIREBASE_CREDENTIALS_JSON = '{"type":"service_account",...}'
$env:DB_BACKEND = "firestore"
```

### Option 3: Application Default Credentials
```powershell
gcloud auth application-default login
$env:DB_BACKEND = "firestore"
```

## Troubleshooting

**Error: "Firebase credentials not found"**
- Solution: Use SQLite for local development (`DB_BACKEND=sqlite`)
- Or set up Firebase credentials as shown above

**Error: "SQLite repository is not available"**
- Solution: SQLite should be available by default in Python
- Check if you're in the correct directory
