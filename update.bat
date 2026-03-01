@echo off
REM Simple incremental bloodwork update script
REM Usage: update.bat biomarkers-export-2026-02-25.csv

if "%1"=="" (
    echo Usage: update.bat ^<csv-filename^>
    echo Example: update.bat biomarkers-export-2026-02-25.csv
    exit /b 1
)

echo ========================================
echo Incremental Bloodwork Update
echo CSV File: %1
echo ========================================
echo.

echo Step 1/4: Generating URLs for new dates...
python update_incremental.py --input %1
if errorlevel 1 (
    echo ERROR: Failed to generate URLs
    exit /b 1
)
echo.

echo Step 2/4: Processing Bortz ages (Selenium)...
python process_batch_urls.py --incremental --headless
if errorlevel 1 (
    echo ERROR: Failed to process Bortz URLs
    exit /b 1
)
echo.

echo Step 3/4: Processing Levine ages (Selenium)...
python process_levine_batch_urls.py --incremental --headless
if errorlevel 1 (
    echo ERROR: Failed to process Levine URLs
    exit /b 1
)
echo.

echo Step 4/4: Regenerating visualization...
powershell -ExecutionPolicy Bypass -File Quick-Visualize.ps1
echo.

echo ========================================
echo Update Complete!
echo ========================================
pause
