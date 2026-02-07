@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo Azure Blob Storage File Transfer - Installation & Setup
echo ============================================================
echo.

echo Checking system requirements...
echo.

REM Check if Python is installed
echo Checking for Python installation...
powershell -Command "Get-Command python3 -ErrorAction SilentlyContinue" >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Python 3 found
    for /f "delims=" %%i in ('powershell -Command "(python3.exe --version 2^>^&1)"') do set PYTHON_VERSION=%%i
    echo      !PYTHON_VERSION!
) else (
    echo [ERROR] Python 3 not found
    echo.
    echo To install Python:
    echo 1. Open: https://www.python.org/downloads/
    echo 2. Download Python 3.11 or later
    echo 3. Run installer and check "Add Python to PATH"
    echo 4. Restart this terminal
    echo.
    pause
    exit /b 1
)

echo.
echo Installation Steps:
echo ============================================================
echo.

echo Step 1: Creating project directories...
if not exist uploads (
    mkdir uploads
    echo  [OK] Created uploads directory
) else (
    echo  [OK] uploads directory exists
)

if not exist downloads (
    mkdir downloads
    echo  [OK] Created downloads directory
) else (
    echo  [OK] downloads directory exists
)

if not exist logs (
    mkdir logs
    echo  [OK] Created logs directory
) else (
    echo  [OK] logs directory exists
)

echo.
echo Step 2: Installing Python dependencies...
echo Installing: azure-storage-blob python-dotenv...
echo.

python3.exe -m pip install --upgrade pip
python3.exe -m pip install -r requirements.txt

if !errorlevel! equ 0 (
    echo [OK] Dependencies installed successfully
) else (
    echo [ERROR] Failed to install dependencies
    echo Try running manually:
    echo   python3 -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Step 3: Checking configuration...

if exist .env (
    echo [OK] .env file exists
    
    REM Check if placeholder values are still there
    findstr /M "YOUR_ACCOUNT_NAME" .env >nul
    if !errorlevel! equ 0 (
        echo [WARNING] .env contains placeholder values!
        echo.
        echo Please edit .env and replace:
        echo - YOUR_ACCOUNT_NAME with your Azure Storage account name
        echo - YOUR_ACCOUNT_KEY with your Azure Storage account key
        echo.
        pause
    )
) else (
    echo [ERROR] .env file not found
)

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.

echo Next Steps:
echo 1. Edit .env file with your Azure credentials
echo 2. Add files to the 'uploads' directory
echo 3. Run the application:
echo.
echo    python3 app.py --help
echo.
echo To upload files:
echo    python3 app.py upload-dir --local-path uploads
echo.

pause
