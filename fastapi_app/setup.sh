#!/bin/bash
set -e

echo "Setting up FastAPI Auth Showcase..."

cd "$(dirname "$0")"

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt --quiet

echo ""
echo "FastAPI setup complete."
echo "Run: source .venv/bin/activate && uvicorn main:app --reload --port 8001"