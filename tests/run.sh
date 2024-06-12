#!/bin/bash

source ../backend/.env
echo "Using conn string ${SPECUIMDBCONNSTR}"

/usr/bin/python3 load.py ${SPECUIMDBCONNSTR}