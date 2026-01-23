@echo off
REM Simple batch file to run the complete bloodwork analysis workflow
REM Usage: run.bat [csv_filename]

setlocal

if "%~1"=="" (
    set CSV_FILE=bloodwork.csv
) else (
    set CSV_FILE=%~1
)

echo.
echo ========================================
echo  Bloodwork Analysis Pipeline
echo ========================================
echo.
echo Input CSV: %CSV_FILE%
echo.

REM Step 1: Generate URLs
echo [1/4] Generating Bortz Calculator URLs...
python generate_batch_urls.py --input "%CSV_FILE%"
if errorlevel 1 (
    echo ERROR: Failed to generate URLs
    pause
    exit /b 1
)

REM Step 2: Process URLs with Selenium
echo.
echo [2/4] Processing URLs with browser automation...
echo This will take a few minutes...
python process_batch_urls.py
if errorlevel 1 (
    echo ERROR: Failed to process URLs
    pause
    exit /b 1
)

REM Step 3: Generate visualization
echo.
echo [3/4] Generating visualization dashboard...
python visualize_age.py
if errorlevel 1 (
    echo ERROR: Failed to generate visualization
    pause
    exit /b 1
)

REM Step 4: Open in browser
echo.
echo [4/4] Opening dashboard in browser...
start age_trend.html

echo.
echo ========================================
echo  SUCCESS! Dashboard opened.
echo ========================================
echo.
echo Generated files:
echo   - batch_urls.json
echo   - age_history.csv
echo   - age_trend.html
echo.
pause
