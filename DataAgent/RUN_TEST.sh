#!/bin/bash
# Quick Test Script for DataAgent Project
# Tests the full project pipeline with the COVID dataset

echo "=========================================="
echo "DataAgent - Full Project Test"
echo "=========================================="
echo ""

cd /home/forhad/Study/personal/projects/DataAgent

echo "Step 1: Running Test Agent..."
python agents/testAgent.py
echo ""

echo "Step 2: Running Full Analysis Pipeline..."
python main.py --data datasets/bq-results-covid-open-data.csv --mode full --target cumulative_confirmed
echo ""

echo "=========================================="
echo "Test Complete!"
echo "Check reports/ directory for generated reports"
echo "Check models/ directory for saved models"
echo "=========================================="
