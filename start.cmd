@echo off
REM Azure Blob Storage File Transfer - Windows Quick Start Script
REM Usage: start.cmd [command] [options]

setlocal enabledelayedexpansion

REM Colors simulation (using title for visual feedback)
set GREEN=[OK]
set RED=[ERROR]
set YELLOW=[WARN]

REM Check if .env exists
if not exist .env (
    echo %YELLOW% .env file not found!
    echo Creating .env from template...
    copy .env.example .env
    echo %YELLOW% Please edit .env with your Azure credentials
    exit /b 1
)

REM Load .env variables
for /f "tokens=*" %%a in (.env) do (
    if "!%%a!"=="" (
        continue
    ) else (
        set %%a
    )
)

REM Check required variables
if "!AZURE_STORAGE_CONNECTION_STRING!"=="" (
    echo %RED% AZURE_STORAGE_CONNECTION_STRING not set in .env
    exit /b 1
)

if "!AZURE_CONTAINER_NAME!"=="" (
    echo %RED% AZURE_CONTAINER_NAME not set in .env
    exit /b 1
)

REM Create required directories
if not exist uploads mkdir uploads
if not exist downloads mkdir downloads
if not exist logs mkdir logs

REM Display menu if no arguments
if "%1"=="" (
    echo.
    echo Azure Blob Storage File Transfer
    echo.
    echo Usage: start.cmd [command] [options]
    echo.
    echo Commands:
    echo   start.cmd upload          - Upload files from uploads/ directory
    echo   start.cmd list [prefix]  - List files in storage
    echo   start.cmd shell          - Start interactive shell
    echo   start.cmd build          - Build Docker image
    echo   start.cmd compose        - Run with docker-compose
    echo.
    exit /b 0
)

REM Parse commands
if "%1"=="upload" (
    echo Uploading files from uploads/ directory...
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c/%%a/%%b)
    docker-compose run --rm file-transfer upload-dir --local-path /app/uploads --blob-prefix !mydate!
    echo Upload complete
) else if "%1"=="list" (
    echo Listing files...
    docker-compose run --rm file-transfer list --blob-prefix %2%
) else if "%1"=="shell" (
    echo Starting interactive shell...
    docker-compose run --rm file-transfer cmd /c bash
) else if "%1"=="build" (
    echo Building Docker image...
    docker-compose build
    echo Build complete
) else if "%1"=="compose" (
    docker-compose %*
) else (
    echo Unknown command: %1
    echo Use 'start.cmd' for help
    exit /b 1
)

endlocal
