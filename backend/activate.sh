#!/bin/bash
source .env
echo "Using conn string ${SPECUIMDBCONNSTR}"

source venv/bin/activate ${SPECUIMDBCONNSTR}
export PYTHONPATH=$PWD
pip install -r requirements.txt

python main.py