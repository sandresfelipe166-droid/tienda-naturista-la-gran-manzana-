# PowerShell script to activate virtual environment and run pytest

# Activate the virtual environment
& .\venv\Scripts\Activate.ps1

# Run pytest with options
pytest --maxfail=1 --disable-warnings -q
