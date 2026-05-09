# Start the Augmented Scoring Service (port 8008)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Set-Location -Path "$projectRoot\services\augmented_scoring"

# Try to activate virtual environment
if (Test-Path "..\..\.venv\Scripts\activate") {
    & "..\..\.venv\Scripts\activate"
} elseif (Test-Path "..\..\venv\Scripts\activate") {
    & "..\..\venv\Scripts\activate"
}

python -m uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload
