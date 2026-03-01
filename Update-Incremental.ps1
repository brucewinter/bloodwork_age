<#
.SYNOPSIS
    Incremental bloodwork update - add new data without reprocessing history

.DESCRIPTION
    This script automates the 4-step incremental workflow:
    1. Generate URLs for new dates only
    2. Process Bortz ages with Selenium
    3. Process Levine ages with Selenium
    4. Regenerate combined visualization

.PARAMETER InputCsv
    Path to the CSV file with new bloodwork data

.PARAMETER Calculator
    Which calculator to update: Bortz, Levine, or Both (default: Both)

.PARAMETER NoVisualization
    Skip visualization regeneration step

.PARAMETER Verbose
    Enable verbose logging

.EXAMPLE
    .\Update-Incremental.ps1 biomarkers-export-2026-02-25.csv
    Process new data from specified CSV file

.EXAMPLE
    .\Update-Incremental.ps1 -InputCsv data.csv -Calculator Bortz -Verbose
    Process only Bortz calculator with verbose logging

.EXAMPLE
    .\Update-Incremental.ps1 data.csv -NoVisualization
    Process data but skip opening the dashboard
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [string]$InputCsv,

    [Parameter()]
    [ValidateSet("Bortz", "Levine", "Both")]
    [string]$Calculator = "Both",

    [switch]$NoVisualization,

    [switch]$VerboseLogging
)

# Color formatting functions
function Write-Step {
    param([string]$Message, [int]$Step, [int]$Total)
    Write-Host "`n==> Step $Step/$Total : $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Script header
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║         Incremental Bloodwork Update Pipeline              ║
║              Add New Data Without Reprocessing             ║
╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Change to script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Host "Working directory: $ScriptDir" -ForegroundColor Gray
Write-Host "Input CSV file: $InputCsv`n" -ForegroundColor Gray

# Validate input file
if (-not (Test-Path $InputCsv)) {
    Write-Error-Custom "CSV file not found: $InputCsv"
    Write-Host ""
    Write-Host "Usage: .\Update-Incremental.ps1 <csv-filename>" -ForegroundColor Yellow
    Write-Host "Example: .\Update-Incremental.ps1 biomarkers-export-2026-02-25.csv" -ForegroundColor Yellow
    exit 1
}

Write-Success "Found input CSV: $InputCsv"

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python detected: $pythonVersion"
} catch {
    Write-Error-Custom "Python not found. Please install Python 3.6+"
    exit 1
}

# Build verbose flag
$verboseFlag = if ($VerboseLogging) { "--verbose" } else { "" }

# Determine which calculators to run
$runBortz = ($Calculator -eq "Bortz") -or ($Calculator -eq "Both")
$runLevine = ($Calculator -eq "Levine") -or ($Calculator -eq "Both")

# Step 1: Generate URLs for new dates
Write-Step "Generating URLs for new dates" 1 4
Write-Host "  Input: $InputCsv" -ForegroundColor Gray
Write-Host "  Calculator: $Calculator" -ForegroundColor Gray
Write-Host ""

$args1 = @("update_incremental.py", "--input", $InputCsv, "--calculator", $Calculator)
if ($verboseFlag) { $args1 += $verboseFlag }

$result = & python $args1 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Success "URL generation complete"

    # Parse output for new date count
    $output = $result -join "`n"
    if ($output -match "Added (\d+) new") {
        Write-Host "  New dates added to batch URLs" -ForegroundColor Gray
    }
} else {
    Write-Error-Custom "Failed to generate URLs"
    Write-Host $result -ForegroundColor Red
    exit 1
}

# Step 2: Process Bortz URLs
if ($runBortz) {
    Write-Step "Processing Bortz ages with Selenium" 2 4
    Write-Host "  Mode: Incremental (new dates only)" -ForegroundColor Gray
    Write-Host "  Browser: Headless" -ForegroundColor Gray
    Write-Host ""

    $args2 = @("process_batch_urls.py", "--incremental", "--headless")
    if ($verboseFlag) { $args2 += $verboseFlag }

    $startTime = Get-Date
    $result = & python $args2 2>&1
    $elapsed = (Get-Date) - $startTime

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Bortz processing complete"
        Write-Host "  Time elapsed: $($elapsed.ToString('mm\:ss'))" -ForegroundColor Gray
    } else {
        Write-Error-Custom "Failed to process Bortz URLs"
        Write-Host $result -ForegroundColor Red
        exit 1
    }
}

# Step 3: Process Levine URLs
if ($runLevine) {
    Write-Step "Processing Levine ages with Selenium" 3 4
    Write-Host "  Mode: Incremental (new dates only)" -ForegroundColor Gray
    Write-Host "  Browser: Headless" -ForegroundColor Gray
    Write-Host ""

    $args3 = @("process_levine_batch_urls.py", "--incremental", "--headless")
    if ($verboseFlag) { $args3 += $verboseFlag }

    $startTime = Get-Date
    $result = & python $args3 2>&1
    $elapsed = (Get-Date) - $startTime

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Levine processing complete"
        Write-Host "  Time elapsed: $($elapsed.ToString('mm\:ss'))" -ForegroundColor Gray
    } else {
        Write-Error-Custom "Failed to process Levine URLs"
        Write-Host $result -ForegroundColor Red
        exit 1
    }
}

# Step 4: Regenerate visualization
if (-not $NoVisualization) {
    Write-Step "Regenerating visualization" 4 4
    Write-Host ""

    $result = & powershell -ExecutionPolicy Bypass -File Quick-Visualize.ps1 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Visualization regenerated and opened in browser"
    } else {
        Write-Error-Custom "Failed to regenerate visualization"
        Write-Host $result -ForegroundColor Red
    }
} else {
    Write-Host "`nSkipping visualization (--NoVisualization flag)" -ForegroundColor Yellow
}

# Summary
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║                  Update Complete!                          ║
╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "Files updated:" -ForegroundColor Cyan
if ($runBortz) {
    Write-Host "  - batch_urls.json          (new Bortz URLs appended)" -ForegroundColor Gray
    Write-Host "  - age_history.csv          (new Bortz ages appended)" -ForegroundColor Gray
}
if ($runLevine) {
    Write-Host "  - levine_batch_urls.json   (new Levine URLs appended)" -ForegroundColor Gray
    Write-Host "  - levine_age_history.csv   (new Levine ages appended)" -ForegroundColor Gray
}
if (-not $NoVisualization) {
    Write-Host "  - combined_age_trend.html  (updated dashboard)" -ForegroundColor Gray
}

Write-Host "`nYour biological age trends have been updated!" -ForegroundColor Cyan
Write-Host ""
