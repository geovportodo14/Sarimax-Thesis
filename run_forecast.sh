#!/bin/bash
# run_forecast.sh - Utility to run the forecasting pipeline

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the pipeline using the local virtual environment
"${SCRIPT_DIR}/.venv/bin/python" "${SCRIPT_DIR}/backend/forecasting/run_pipeline.py" "$@"
