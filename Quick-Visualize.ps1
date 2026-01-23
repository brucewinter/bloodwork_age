<#
.SYNOPSIS
    Quick visualization regeneration (skips URL generation and Selenium)

.DESCRIPTION
    Use this when you already have age history CSV files and just want to
    regenerate the visualization with updated styling or after config changes.

.PARAMETER Calculator
    Which calculator(s) to visualize: "Bortz", "Levine", or "Both" (default: Both)

.EXAMPLE
    .\Quick-Visualize.ps1
    Regenerate combined visualization and open in browser

.EXAMPLE
    .\Quick-Visualize.ps1 -Calculator Bortz
    Regenerate only Bortz visualization
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet("Bortz", "Levine", "Both")]
    [string]$Calculator = "Both"
)

$runBortz = ($Calculator -eq "Bortz") -or ($Calculator -eq "Both")
$runLevine = ($Calculator -eq "Levine") -or ($Calculator -eq "Both")

Write-Host "`n==> Regenerating visualization from existing CSV files`n" -ForegroundColor Cyan

# Check required files exist
if ($runBortz -and -not (Test-Path "age_history.csv")) {
    Write-Host "[ERROR] age_history.csv not found!" -ForegroundColor Red
    Write-Host "  Run the full pipeline first: .\Run-BloodworkAnalysis.ps1" -ForegroundColor Yellow
    exit 1
}

if ($runLevine -and -not (Test-Path "levine_age_history.csv")) {
    Write-Host "[ERROR] levine_age_history.csv not found!" -ForegroundColor Red
    Write-Host "  Run the full pipeline first: .\Run-BloodworkAnalysis.ps1" -ForegroundColor Yellow
    exit 1
}

# Generate appropriate visualization
if ($Calculator -eq "Both") {
    Write-Host "Generating combined dashboard..." -ForegroundColor Gray
    python visualize_combined_age.py
    $outputFile = "combined_age_trend.html"
} elseif ($Calculator -eq "Bortz") {
    Write-Host "Generating Bortz dashboard..." -ForegroundColor Gray
    python visualize_age.py
    $outputFile = "age_trend.html"
} else {
    Write-Host "[ERROR] Levine-only visualization not yet implemented" -ForegroundColor Red
    Write-Host "  Use -Calculator Both for combined dashboard" -ForegroundColor Yellow
    exit 1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Visualization regenerated successfully!" -ForegroundColor Green
    Start-Process $outputFile
    Write-Host "[SUCCESS] Opened in browser`n" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Failed to generate visualization`n" -ForegroundColor Red
    exit 1
}
