#!/bin/bash
set -e
echo "🔧 Setting up MCP Weather Server..."
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Setup complete!"
echo ""
echo "Run with stdio:   python weather_server.py"
echo "Run with HTTP:    python weather_server.py --transport streamable-http --port 8000"
echo "Test client:      python client_example.py"
