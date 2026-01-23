<#
.SYNOPSIS
    Automated bloodwork analysis workflow - from CSV to visualization

.DESCRIPTION
    This script automates the complete workflow:
    1. Generates Bortz Calculator URLs from bloodwork CSV
    2. Processes URLs to extract biological ages (automated with Selenium)
    3. Generates interactive visualization dashboard
    4. Opens the results in your browser

.PARAMETER InputCsv
    Path to the bloodwork CSV file (default: bloodwork.csv)

.PARAMETER SkipUrlGeneration
    Skip generating batch URLs if batch_urls.json already exists

.PARAMETER SkipSelenium
    Skip Selenium automation (use if age_history.csv is already up-to-date)

.PARAMETER VerboseLogging
    Enable verbose logging for all scripts

.PARAMETER Headless
    Run browser automation in headless mode (no GUI)

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1
    Run complete workflow with default bloodwork.csv

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1 -InputCsv "my_bloodwork_2024.csv"
    Run with a custom CSV file

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1 -SkipSelenium
    Skip Selenium automation and just regenerate visualization

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1 -VerboseLogging -Headless
    Run with verbose logging and headless browser
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$InputCsv = "bloodwork.csv",

    [switch]$SkipUrlGeneration,

    [switch]$SkipSelenium,

    [switch]$VerboseLogging,

    [switch]$Headless
)

# Color formatting functions
function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# Script header
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║         Bloodwork Biological Age Analysis Pipeline         ║
║                    Automated Workflow                       ║
╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Change to script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Host "Working directory: $ScriptDir`n" -ForegroundColor Gray

# Validate input CSV exists (only if we need it)
if (-not $SkipUrlGeneration) {
    if (-not (Test-Path $InputCsv)) {
        Write-Error-Custom "Input CSV file not found: $InputCsv"
        Write-Host "`nPlease provide a valid CSV file path." -ForegroundColor Yellow
        exit 1
    }
    Write-Success "Found input CSV: $InputCsv"
}

# Check Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python detected: $pythonVersion"
} catch {
    Write-Error-Custom "Python not found. Please install Python 3.6+ and add it to PATH."
    exit 1
}

# Check if config.py has birthdate set
Write-Step "Validating configuration"
$configContent = Get-Content "config.py" -Raw
if ($configContent -match 'BIRTHDATE = "(\d{4}-\d{2}-\d{2})"') {
    $birthdate = $matches[1]
    if ($birthdate -eq "1965-01-01") {
        Write-Warning-Custom "BIRTHDATE in config.py appears to be the default placeholder."
        Write-Host "  Please update config.py with your actual birthdate." -ForegroundColor Yellow
        $continue = Read-Host "  Continue anyway? (y/n)"
        if ($continue -ne "y") {
            exit 0
        }
    } else {
        Write-Success "Birthdate configured: $birthdate"
    }
} else {
    Write-Warning-Custom "Could not validate BIRTHDATE in config.py"
}

# Build verbose flag
$verboseFlag = if ($VerboseLogging) { "--verbose" } else { "" }

# Step 1: Generate Batch URLs
if (-not $SkipUrlGeneration) {
    Write-Step "Step 1: Generating Bortz Calculator URLs"
    Write-Host "  Input: $InputCsv" -ForegroundColor Gray
    Write-Host "  Output: batch_urls.json" -ForegroundColor Gray

    $args1 = @("generate_batch_urls.py", "--input", $InputCsv)
    if ($verboseFlag) { $args1 += $verboseFlag }

    $result = & python $args1 2>&1

    if ($LASTEXITCODE -eq 0) {
        # Parse output for URL count
        if ($result -match "Generated (\d+) URL") {
            $urlCount = $matches[1]
            Write-Success "Generated $urlCount URLs successfully"
        } else {
            Write-Success "URLs generated successfully"
        }
    } else {
        Write-Error-Custom "Failed to generate URLs"
        Write-Host $result -ForegroundColor Red
        exit 1
    }
} else {
    Write-Step "Step 1: Skipping URL generation (using existing batch_urls.json)"
    if (-not (Test-Path "batch_urls.json")) {
        Write-Error-Custom "batch_urls.json not found. Cannot skip URL generation."
        exit 1
    }
}

# Step 2: Process URLs with Selenium
if (-not $SkipSelenium) {
    Write-Step "Step 2: Processing URLs to extract biological ages"
    Write-Host "  This will open Chrome and automatically extract ages from each URL" -ForegroundColor Gray
    Write-Host "  Input: batch_urls.json" -ForegroundColor Gray
    Write-Host "  Output: age_history.csv" -ForegroundColor Gray

    # Check if Selenium is installed
    $seleniumCheck = & python -c "import selenium" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning-Custom "Selenium not installed. Installing..."
        & pip install selenium
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Failed to install Selenium"
            exit 1
        }
    }

    $args2 = @("process_batch_urls.py")
    if ($verboseFlag) { $args2 += $verboseFlag }
    if ($Headless) { $args2 += "--headless" }

    Write-Host "`n  Starting browser automation..." -ForegroundColor Yellow
    $startTime = Get-Date

    $result = & python $args2 2>&1

    $elapsed = (Get-Date) - $startTime

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Extracted biological ages successfully"
        Write-Host "  Time elapsed: $($elapsed.ToString('mm\:ss'))" -ForegroundColor Gray
    } else {
        Write-Error-Custom "Failed to process URLs"
        Write-Host $result -ForegroundColor Red
        Write-Host "`nTip: Use -SkipSelenium if you already have age_history.csv" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Step "Step 2: Skipping Selenium automation (using existing age_history.csv)"
    if (-not (Test-Path "age_history.csv")) {
        Write-Error-Custom "age_history.csv not found. Cannot skip Selenium automation."
        exit 1
    }
}

# Step 3: Generate Visualization
Write-Step "Step 3: Generating interactive visualization dashboard"
Write-Host "  Input: age_history.csv" -ForegroundColor Gray
Write-Host "  Output: age_trend.html" -ForegroundColor Gray

$args3 = @("visualize_age.py")
if ($verboseFlag) { $args3 += $verboseFlag }

$result = & python $args3 2>&1

if ($LASTEXITCODE -eq 0) {
    # Parse output for data point count
    if ($result -match "Loaded (\d+) data point") {
        $dataPoints = $matches[1]
        Write-Success "Generated visualization with $dataPoints data points"
    } else {
        Write-Success "Visualization generated successfully"
    }
} else {
    Write-Error-Custom "Failed to generate visualization"
    Write-Host $result -ForegroundColor Red
    exit 1
}

# Step 4: Open visualization
Write-Step "Step 4: Opening visualization in browser"

if (Test-Path "age_trend.html") {
    Start-Process "age_trend.html"
    Write-Success "Dashboard opened in your default browser"
} else {
    Write-Error-Custom "age_trend.html not found"
    exit 1
}

# Summary
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║                   Pipeline Complete!                       ║
╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "Generated files:" -ForegroundColor Cyan
Write-Host "  - batch_urls.json      - Bortz Calculator URLs" -ForegroundColor Gray
Write-Host "  - age_history.csv      - Extracted biological ages" -ForegroundColor Gray
Write-Host "  - age_trend.html       - Interactive dashboard" -ForegroundColor Gray

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  - Review your biological age trends in the browser" -ForegroundColor Gray
Write-Host "  - Check the Age Delta chart to see aging trajectory" -ForegroundColor Gray
Write-Host "  - Green points = biological age younger than chronological (good)" -ForegroundColor Gray
Write-Host "  - Pink points = biological age older than chronological" -ForegroundColor Gray

Write-Host "`nTip: Run with -SkipSelenium to quickly regenerate visualization" -ForegroundColor Yellow
Write-Host ""
