Param(
    [string]$Project = "backend" # or "frontend" or "all"
)

Write-Host "Setup dev environment: $Project"

if ($Project -eq 'backend' -or $Project -eq 'all') {
    Write-Host "Setting up backend environment..."
    python -m venv .venv
    & .\.venv\Scripts\Activate.ps1
    pip install -U pip
    pip install -r inventario-backend\requirements.txt
    Write-Host "Backend venv created and dependencies installed. Use: & .\.venv\Scripts\Activate.ps1 to activate."
}

if ($Project -eq 'frontend' -or $Project -eq 'all') {
    Write-Host "Setting up frontend environment..."
    Push-Location inventario-frontend
    # create frontend venv for Python tools if using pyright/ruff
    python -m venv .venv
    & .\.venv\Scripts\Activate.ps1
    pip install -U pip
    if (Test-Path ..\inventario-frontend\requirements.txt) {
        pip install -r ..\inventario-frontend\requirements.txt
    }
    # Node dependencies
    if (Test-Path package.json) {
        if (Get-Command npm -ErrorAction SilentlyContinue) {
            npm install
        } else {
            Write-Host "npm not found - Please install Node.js to run frontend tooling (npm install)."
        }
    }
    Pop-Location
    Write-Host "Frontend environment: Node + Python tools may be installed."
}

Write-Host "Setup script finished."
