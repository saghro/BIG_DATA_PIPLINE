#!/bin/bash
# Script to run the Streamlit Dashboard

echo "🐘 Starting Mastodon Dashboard..."
echo "================================="

# Check if streamlit is installed
if ! pip show streamlit > /dev/null 2>&1; then
    echo "📦 Installing Streamlit & Dependencies..."
    pip install streamlit pandas cassandra-driver altair
fi

echo ""
echo "🚀 Launching Dashboard on http://localhost:8501"
echo "   (Press Ctrl+C to stop)"
echo ""

python3 -m streamlit run dashboard.py
