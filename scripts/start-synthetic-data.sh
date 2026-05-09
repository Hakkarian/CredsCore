#!/bin/bash
# Synthetic Data Service Startup Script
# Port: 8007

set -e

SERVICE_NAME="Synthetic Data Service"
PORT=8007
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$SCRIPT_DIR/../services/synthetic-data"

echo "========================================="
echo " Starting $SERVICE_NAME"
echo " Port: $PORT"
echo "========================================="

# Create models directory if it doesn't exist
mkdir -p "$SERVICE_DIR/models"

# Change to service directory
cd "$SERVICE_DIR"

# Check dependencies
echo "Checking dependencies..."
if ! python -c "import fastapi, ctgan, pandas, torch" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the service
echo "Starting $SERVICE_NAME on port $PORT..."
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
