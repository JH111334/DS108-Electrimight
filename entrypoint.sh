#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-streamlit}"

case "$MODE" in
  streamlit)
    exec streamlit run streamlit_ui/app.py \
      --server.address=0.0.0.0 \
      --server.port=8501 \
      --server.headless=true
    ;;
  pipeline)
    exec python -m src.gold.pipeline
    ;;
  pipeline-full)
    exec python -m src.run_all --with-gan
    ;;
  audit)
    exec python -m src.bronze.data_quality_audit
    ;;
  assertions)
    exec python -m src.data_assertions
    ;;
  leakage)
    exec python -m src.leakage_audit
    ;;
  missingness)
    exec python -m src.missingness_analysis
    ;;
  test)
    exec python -m pytest -v
    ;;
  jupyter)
    exec jupyter lab \
      --ip=0.0.0.0 \
      --port=8888 \
      --no-browser \
      --ServerApp.token='' \
      --notebook-dir=/app/notebooks
    ;;
  shell | bash)
    shift
    exec /bin/bash "$@"
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo "Valid modes: streamlit, pipeline, pipeline-full, audit, assertions, leakage, missingness, test, jupyter, shell"
    exit 1
    ;;
esac
