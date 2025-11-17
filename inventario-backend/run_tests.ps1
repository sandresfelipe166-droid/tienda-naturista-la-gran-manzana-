# PowerShell script to activate virtual environment and run pytest
# Improved version with options for different test scenarios

param(
    [switch]$Integration,  # Include integration tests
    [switch]$Coverage,     # Run with coverage report
    [switch]$Verbose,      # Verbose output
    [switch]$Fast          # Fast mode (stop on first failure)
)

Write-Host "=== Inventario Backend - Test Runner ===" -ForegroundColor Cyan
Write-Host ""

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Build pytest command
$pytestCmd = "pytest"

# Base options
$options = @()

if ($Verbose) {
    $options += "-vv"
} else {
    $options += "-v"
}

# Integration tests
if ($Integration) {
    Write-Host "Running ALL tests (including integration tests)..." -ForegroundColor Green
    Write-Host "Note: Redis must be running for integration tests" -ForegroundColor Yellow
    $options += "-m", ""  # Run all tests
} else {
    Write-Host "Running unit tests only (excluding integration tests)..." -ForegroundColor Green
    # Default behavior from pytest.ini: -m "not integration"
}

# Coverage
if ($Coverage) {
    Write-Host "Coverage report will be generated" -ForegroundColor Yellow
    $options += "--cov=app", "--cov-report=html", "--cov-report=term"
}

# Fast mode
if ($Fast) {
    $options += "--maxfail=1", "-x"
}

# Add warnings control
$options += "--disable-warnings"

# Execute pytest
Write-Host ""
Write-Host "Executing: $pytestCmd $($options -join ' ')" -ForegroundColor Cyan
Write-Host ""

& $pytestCmd @options

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "Usage examples:" -ForegroundColor Cyan
Write-Host "  .\run_tests.ps1                  # Run unit tests only"
Write-Host "  .\run_tests.ps1 -Integration     # Run all tests (requires Redis)"
Write-Host "  .\run_tests.ps1 -Coverage        # Run with coverage report"
Write-Host "  .\run_tests.ps1 -Fast            # Stop on first failure"
Write-Host "  .\run_tests.ps1 -Verbose         # Verbose output"
Write-Host ""

exit $exitCode
