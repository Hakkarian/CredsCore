#!/bin/bash
# Start the Augmented Scoring Service (port 8008)

cd "$(dirname "$0")/.."

cd services/augmented_scoring

source ../../.venv/bin/activate 2>/dev/null || source ../../venv/bin/activate 2>/dev/null || echo "Using system Python"

python -m uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload
