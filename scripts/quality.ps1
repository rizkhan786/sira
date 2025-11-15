# SIRA Code Quality Script
# Run code quality checks: formatting, linting, and type checking

param(
    [switch]$Format,
    [switch]$Lint,
    [switch]$TypeCheck,
    [switch]$Test,
    [switch]$All
)

$ErrorActionPreference = "Stop"

Write-Host "SIRA Code Quality Tools" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host ""

# Main execution
if ($Format -or $All) {
    Write-Host "Formatting code with black..." -ForegroundColor Yellow
    docker exec sira-api-dev black src/
    
    Write-Host "Sorting imports with isort..." -ForegroundColor Yellow
    docker exec sira-api-dev isort src/
    
    Write-Host "✓ Code formatted successfully!" -ForegroundColor Green
    Write-Host ""
}

if ($Lint -or $All) {
    Write-Host "Running ruff linter..." -ForegroundColor Yellow
    docker exec sira-api-dev ruff check src/ --fix
    
    Write-Host "✓ Linting completed!" -ForegroundColor Green
    Write-Host ""
}

if ($TypeCheck -or $All) {
    Write-Host "Running mypy type checker..." -ForegroundColor Yellow
    docker exec sira-api-dev mypy src/
    
    Write-Host "✓ Type checking completed!" -ForegroundColor Green
    Write-Host ""
}

if ($Test -or $All) {
    Write-Host "Running pytest..." -ForegroundColor Yellow
    docker exec sira-api-dev pytest tests/ -v
    
    Write-Host "✓ Tests completed!" -ForegroundColor Green
    Write-Host ""
}

if (-not ($Format -or $Lint -or $TypeCheck -or $Test -or $All)) {
    Write-Host "Usage: .\scripts\quality.ps1 [-Format] [-Lint] [-TypeCheck] [-Test] [-All]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Format     Format code with black and isort"
    Write-Host "  -Lint       Run ruff linter"
    Write-Host "  -TypeCheck  Run mypy type checker"
    Write-Host "  -Test       Run pytest tests"
    Write-Host "  -All        Run all quality checks"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\scripts\quality.ps1 -Format"
    Write-Host "  .\scripts\quality.ps1 -Lint -TypeCheck"
    Write-Host "  .\scripts\quality.ps1 -All"
    exit 1
}

Write-Host "All requested checks completed!" -ForegroundColor Green
