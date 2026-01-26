#!/bin/bash
# Script to kill any running dashboard processes on port 8050

echo "Checking for processes on port 8050..."

# Find processes using port 8050
PIDS=$(lsof -ti :8050 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✓ No processes found on port 8050"
    exit 0
fi

echo "Found processes: $PIDS"
echo "Killing processes..."

# Kill all processes
for PID in $PIDS; do
    kill -9 $PID 2>/dev/null
    echo "  ✓ Killed process $PID"
done

sleep 1

# Verify port is free
if lsof -ti :8050 >/dev/null 2>&1; then
    echo "⚠ Warning: Port 8050 may still be in use"
else
    echo "✓ Port 8050 is now free"
fi
