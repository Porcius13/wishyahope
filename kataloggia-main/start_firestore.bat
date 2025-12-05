@echo off
echo ========================================
echo Firestore ile Uygulama Başlatılıyor
echo ========================================
echo.

REM Ortam değişkenlerini ayarla
set DB_BACKEND=firestore
set FIREBASE_CREDENTIALS_PATH=%~dp0miayis-service-account.json
set FIREBASE_PROJECT_ID=miayis
set PORT=5000
set HOST=0.0.0.0
set DEBUG=True

echo DB_BACKEND: %DB_BACKEND%
echo FIREBASE_PROJECT_ID: %FIREBASE_PROJECT_ID%
echo FIREBASE_CREDENTIALS_PATH: %FIREBASE_CREDENTIALS_PATH%
echo.
echo Uygulama başlatılıyor...
echo URL: http://localhost:5000
echo.

REM Uygulamayı başlat
python run.py

pause

