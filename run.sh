#!/bin/bash

set -e

if [ -d "./venv" ]; then
    PYTHON="./venv/bin/python3"
    STREAMLIT="./venv/bin/streamlit"
else
    PYTHON="python3"
    STREAMLIT="streamlit"
fi

echo "--- Running Data Pipeline ---"
$PYTHON -m src.ingest_data && \
$PYTHON -m src.process_data && \
$PYTHON -m src.analyze_and_alert

echo "--- Starting Dashboard ---"
$STREAMLIT run src/dashboard.py --server.port ${PORT:-8501} --server.address 0.0.0.0
