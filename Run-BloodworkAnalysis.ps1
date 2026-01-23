<#
.SYNOPSIS
    Automated bloodwork analysis workflow - from CSV to visualization

.DESCRIPTION
    This script automates the complete workflow:
    1. Generates Calculator URLs from bloodwork CSV (Bortz and/or Levine)
    2. Processes URLs to extract biological/phenotypic ages (automated with Selenium)
    3. Generates interactive visualization dashboard
    4. Opens the results in your browser

.PARAMETER InputCsv
    Path to the bloodwork CSV file (default: bloodwork.csv)

.PARAMETER Calculator
    Which calculator(s) to run: "Bortz", "Levine", or "Both" (default: Both)

.PARAMETER SkipUrlGeneration
    Skip generating batch URLs if batch_urls.json already exists

.PARAMETER SkipSelenium
    Skip Selenium automation (use if age_history.csv is already up-to-date)

.PARAMETER VerboseLogging
    Enable verbose logging for all scripts

.PARAMETER Headless
    Run browser automation in headless mode (no GUI)

.PARAMETER Help
    Display this help message

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1
    Run complete workflow with both Bortz and Levine calculators

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1 -Help
    Display full help documentation

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1 -InputCsv "my_bloodwork_2024.csv"
    Run with a custom CSV file

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1 -Calculator Bortz
    Run only the Bortz Blood Age Calculator

.EXAMPLE
    .\Run-BloodworkAnalysis.ps1 -Calculator Levine -Headless
    Run only the Levine PhenoAge Calculator in headless mode

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

    [Parameter()]
    [ValidateSet("Bortz", "Levine", "Both")]
    [string]$Calculator = "Both",

    [switch]$SkipUrlGeneration,

    [switch]$SkipSelenium,

    [switch]$VerboseLogging,

    [switch]$Headless,

    [switch]$Help
)

# Handle -Help parameter
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

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
        Write-Host ""
        Write-Host "Usage Examples:" -ForegroundColor Yellow
        Write-Host "  .\Run-BloodworkAnalysis.ps1" -ForegroundColor Gray
        Write-Host "  .\Run-BloodworkAnalysis.ps1 -InputCsv 'my_bloodwork.csv'" -ForegroundColor Gray
        Write-Host "  .\Run-BloodworkAnalysis.ps1 -SkipUrlGeneration -SkipSelenium" -ForegroundColor Gray
        Write-Host ""
        Write-Host "For detailed help, run:" -ForegroundColor Cyan
        Write-Host "  Get-Help .\Run-BloodworkAnalysis.ps1 -Full" -ForegroundColor White
        Write-Host ""
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

# Determine which calculators to run
$runBortz = ($Calculator -eq "Bortz") -or ($Calculator -eq "Both")
$runLevine = ($Calculator -eq "Levine") -or ($Calculator -eq "Both")

# Step 1: Generate Batch URLs
if (-not $SkipUrlGeneration) {
    Write-Step "Step 1: Generating Calculator URLs"

    # Generate Bortz URLs
    if ($runBortz) {
        Write-Host "`n  Bortz Blood Age Calculator:" -ForegroundColor Yellow
        Write-Host "    Input: $InputCsv" -ForegroundColor Gray
        Write-Host "    Output: batch_urls.json" -ForegroundColor Gray

        $args1 = @("generate_batch_urls.py", "--input", $InputCsv)
        if ($verboseFlag) { $args1 += $verboseFlag }

        $result = & python $args1 2>&1

        if ($LASTEXITCODE -eq 0) {
            if ($result -match "Generated (\d+) URL") {
                $bortzUrlCount = $matches[1]
                Write-Success "Generated $bortzUrlCount Bortz URLs successfully"
            } else {
                Write-Success "Bortz URLs generated successfully"
            }
        } else {
            Write-Error-Custom "Failed to generate Bortz URLs"
            Write-Host $result -ForegroundColor Red
            exit 1
        }
    }

    # Generate Levine URLs
    if ($runLevine) {
        Write-Host "`n  Levine PhenoAge Calculator:" -ForegroundColor Yellow
        Write-Host "    Input: $InputCsv" -ForegroundColor Gray
        Write-Host "    Output: levine_batch_urls.json" -ForegroundColor Gray

        $args1b = @("generate_levine_batch_urls.py", "--input", $InputCsv)
        if ($verboseFlag) { $args1b += $verboseFlag }

        $result = & python $args1b 2>&1

        if ($LASTEXITCODE -eq 0) {
            if ($result -match "Generated (\d+) .*URL") {
                $levineUrlCount = $matches[1]
                Write-Success "Generated $levineUrlCount Levine URLs successfully"
            } else {
                Write-Success "Levine URLs generated successfully"
            }
        } else {
            Write-Error-Custom "Failed to generate Levine URLs"
            Write-Host $result -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Step "Step 1: Skipping URL generation (using existing files)"
    if ($runBortz -and -not (Test-Path "batch_urls.json")) {
        Write-Error-Custom "batch_urls.json not found. Cannot skip URL generation."
        exit 1
    }
    if ($runLevine -and -not (Test-Path "levine_batch_urls.json")) {
        Write-Error-Custom "levine_batch_urls.json not found. Cannot skip URL generation."
        exit 1
    }
}

# Step 2: Process URLs with Selenium
if (-not $SkipSelenium) {
    Write-Step "Step 2: Processing URLs to extract ages"
    Write-Host "  This will open Chrome and automatically extract ages from each URL" -ForegroundColor Gray

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

    # Process Bortz URLs
    if ($runBortz) {
        Write-Host "`n  Bortz Blood Age Calculator:" -ForegroundColor Yellow
        Write-Host "    Input: batch_urls.json" -ForegroundColor Gray
        Write-Host "    Output: age_history.csv" -ForegroundColor Gray

        $args2 = @("process_batch_urls.py")
        if ($verboseFlag) { $args2 += $verboseFlag }
        if ($Headless) { $args2 += "--headless" }

        Write-Host "`n    Starting browser automation..." -ForegroundColor Yellow
        $startTime = Get-Date

        $result = & python $args2 2>&1

        $elapsed = (Get-Date) - $startTime

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Extracted Bortz biological ages successfully"
            Write-Host "    Time elapsed: $($elapsed.ToString('mm\:ss'))" -ForegroundColor Gray
        } else {
            Write-Error-Custom "Failed to process Bortz URLs"
            Write-Host $result -ForegroundColor Red
            exit 1
        }
    }

    # Process Levine URLs
    if ($runLevine) {
        Write-Host "`n  Levine PhenoAge Calculator:" -ForegroundColor Yellow
        Write-Host "    Input: levine_batch_urls.json" -ForegroundColor Gray
        Write-Host "    Output: levine_age_history.csv" -ForegroundColor Gray

        $args2b = @("process_levine_batch_urls.py")
        if ($verboseFlag) { $args2b += $verboseFlag }
        if ($Headless) { $args2b += "--headless" }

        Write-Host "`n    Starting browser automation..." -ForegroundColor Yellow
        $startTime = Get-Date

        $result = & python $args2b 2>&1

        $elapsed = (Get-Date) - $startTime

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Extracted Levine phenotypic ages successfully"
            Write-Host "    Time elapsed: $($elapsed.ToString('mm\:ss'))" -ForegroundColor Gray
        } else {
            Write-Error-Custom "Failed to process Levine URLs"
            Write-Host $result -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Step "Step 2: Skipping Selenium automation (using existing files)"
    if ($runBortz -and -not (Test-Path "age_history.csv")) {
        Write-Error-Custom "age_history.csv not found. Cannot skip Selenium automation."
        exit 1
    }
    if ($runLevine -and -not (Test-Path "levine_age_history.csv")) {
        Write-Error-Custom "levine_age_history.csv not found. Cannot skip Selenium automation."
        exit 1
    }
}

# Step 3: Generate Visualization
Write-Step "Step 3: Generating interactive visualization dashboard"

if ($Calculator -eq "Both") {
    # Generate combined visualization
    Write-Host "  Input: age_history.csv, levine_age_history.csv" -ForegroundColor Gray
    Write-Host "  Output: combined_age_trend.html" -ForegroundColor Gray

    $args3 = @("visualize_combined_age.py")
    if ($verboseFlag) { $args3 += $verboseFlag }

    $result = & python $args3 2>&1
    $outputFile = "combined_age_trend.html"

    if ($LASTEXITCODE -eq 0) {
        if ($result -match "Combined (\d+) total measurement") {
            $dataPoints = $matches[1]
            Write-Success "Generated combined visualization with $dataPoints data points"
        } else {
            Write-Success "Combined visualization generated successfully"
        }
    } else {
        Write-Error-Custom "Failed to generate combined visualization"
        Write-Host $result -ForegroundColor Red
        exit 1
    }
} elseif ($Calculator -eq "Bortz") {
    # Generate Bortz-only visualization
    Write-Host "  Input: age_history.csv" -ForegroundColor Gray
    Write-Host "  Output: age_trend.html" -ForegroundColor Gray

    $args3 = @("visualize_age.py")
    if ($verboseFlag) { $args3 += $verboseFlag }

    $result = & python $args3 2>&1
    $outputFile = "age_trend.html"

    if ($LASTEXITCODE -eq 0) {
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
} else {
    # Levine-only - need to create a Levine-specific visualizer (for now, show error)
    Write-Warning-Custom "Levine-only visualization not yet implemented"
    Write-Host "  Tip: Use -Calculator Both to see combined dashboard" -ForegroundColor Yellow
    $outputFile = $null
}

# Step 4: Open visualization
if ($outputFile) {
    Write-Step "Step 4: Opening visualization in browser"

    if (Test-Path $outputFile) {
        Start-Process $outputFile
        Write-Success "Dashboard opened in your default browser"
    } else {
        Write-Error-Custom "$outputFile not found"
        exit 1
    }
}

# Summary
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║                   Pipeline Complete!                       ║
╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "Generated files:" -ForegroundColor Cyan
if ($runBortz) {
    Write-Host "  - batch_urls.json           - Bortz Calculator URLs" -ForegroundColor Gray
    Write-Host "  - age_history.csv           - Extracted biological ages" -ForegroundColor Gray
}
if ($runLevine) {
    Write-Host "  - levine_batch_urls.json    - Levine Calculator URLs" -ForegroundColor Gray
    Write-Host "  - levine_age_history.csv    - Extracted phenotypic ages" -ForegroundColor Gray
}
if ($Calculator -eq "Both") {
    Write-Host "  - combined_age_trend.html   - Combined dashboard" -ForegroundColor Gray
} elseif ($Calculator -eq "Bortz") {
    Write-Host "  - age_trend.html            - Bortz dashboard" -ForegroundColor Gray
}

Write-Host "`nNext steps:" -ForegroundColor Cyan
if ($Calculator -eq "Both") {
    Write-Host "  - Review both calculator results in the combined dashboard" -ForegroundColor Gray
    Write-Host "  - Compare Bortz Blood Age vs Levine PhenoAge trends" -ForegroundColor Gray
    Write-Host "  - Check both delta charts to see aging trajectory" -ForegroundColor Gray
} else {
    Write-Host "  - Review your biological/phenotypic age trends in the browser" -ForegroundColor Gray
    Write-Host "  - Check the Age Delta chart to see aging trajectory" -ForegroundColor Gray
}
Write-Host "  - Green points = age younger than chronological (good)" -ForegroundColor Gray
Write-Host "  - Pink points = age older than chronological" -ForegroundColor Gray

Write-Host "`nTips:" -ForegroundColor Yellow
Write-Host "  - Run with -SkipSelenium to quickly regenerate visualization" -ForegroundColor Gray
Write-Host "  - Use -Calculator Bortz or -Calculator Levine to run single calculator" -ForegroundColor Gray
Write-Host "  - Use -Headless for faster processing without browser window" -ForegroundColor Gray
Write-Host ""
