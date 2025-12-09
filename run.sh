#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e


echo "--- Running Data Pipeline ---"
python src/ingest_data.py && \
python src/process_data.py && \
python src/analyze_and_alert.py

echo "--- Starting Dashboard ---"
streamlit run src/dashboard.py --server.port ${PORT:-8501} --server.address 0.0.0.0
