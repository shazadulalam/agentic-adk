#!/bin/bash
# Script to run the DataAgent Dashboard

cd "$(dirname "$0")"

echo "============================================================"
echo "🚀 Starting DataAgent Dashboard"
echo "============================================================"
echo ""
echo "📊 Dashboard will be available at:"
echo "   → http://localhost:8050"
echo "   → http://127.0.0.1:8050"
echo ""
echo "💡 Tips:"
echo "   - Upload a CSV file or use the default dataset"
echo "   - Select target column for predictions"
echo "   - Click 'Run Full Analysis' to generate results"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

python dashboards/dashboard.py
