#!/bin/bash
# Script to run the Modern BI Dashboard

echo "📊 Starting Modern BI Dashboard..."
echo "================================="

# Check if required packages are installed
if ! pip show streamlit plotly > /dev/null 2>&1; then
    echo "📦 Installing Streamlit & Plotly..."
    pip install streamlit pandas cassandra-driver altair plotly
fi

echo ""
echo "🚀 Launching Modern BI Dashboard on http://localhost:8501"
echo "   (Press Ctrl+C to stop)"
echo ""

python3 -m streamlit run dashboard_bi.py
