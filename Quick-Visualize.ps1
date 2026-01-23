<#
.SYNOPSIS
    Quick visualization regeneration (skips URL generation and Selenium)

.DESCRIPTION
    Use this when you already have age_history.csv and just want to
    regenerate the visualization with updated styling or after config changes.

.EXAMPLE
    .\Quick-Visualize.ps1
    Regenerate visualization and open in browser
#>

Write-Host "`n==> Regenerating visualization from existing age_history.csv`n" -ForegroundColor Cyan

if (-not (Test-Path "age_history.csv")) {
    Write-Host "[ERROR] age_history.csv not found!" -ForegroundColor Red
    Write-Host "  Run the full pipeline first: .\Run-BloodworkAnalysis.ps1" -ForegroundColor Yellow
    exit 1
}

python visualize_age.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Visualization regenerated successfully!" -ForegroundColor Green
    Start-Process "age_trend.html"
    Write-Host "[SUCCESS] Opened in browser`n" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Failed to generate visualization`n" -ForegroundColor Red
    exit 1
}
