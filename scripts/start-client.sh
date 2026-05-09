#!/bin/bash
# Start CredsCore Client (Next.js Frontend)
# Port: 3000

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_DIR="$(dirname "$SCRIPT_DIR")/client"

echo "Starting CredsCore Client..."
echo "URL: http://localhost:3000"
echo ""

cd "$CLIENT_DIR"
npm run dev
