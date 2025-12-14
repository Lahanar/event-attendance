#!/usr/bin/env bash
set -e
python3 -m venv .venv || true
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 3000 --reload
