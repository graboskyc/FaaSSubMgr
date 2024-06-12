#!/bin/bash
source .env
echo "Using conn string ${SPECUIMDBCONNSTR}"
echo "Using master key ${MASTERENCKEYASBASE64}"

source venv/bin/activate ${SPECUIMDBCONNSTR} ${MASTERENCKEYASBASE64}
export PYTHONPATH=$PWD
pip install -r requirements.txt

python main.py