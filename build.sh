#!/bin/bash

echo
echo "+================================"
echo "| START: FaasSubMgr"
echo "+================================"
echo

source backend/.env

datehash=`date | md5sum | cut -d" " -f1`
abbrvhash=${datehash: -8}
echo "Using conn string ${SPECUIMDBCONNSTR}"

echo 
echo "Building container using tag ${abbrvhash}"
echo
docker build -t graboskyc/faassubmgr:latest -t graboskyc/faassubmgr:${abbrvhash} --platform=linux/amd64 .

EXITCODE=$?

if [ $EXITCODE -eq 0 ]
    then

    echo 
    echo "Starting container"
    echo
    docker stop faassubmgr
    docker rm faassubmgr
    docker run -t -i -d -p 8000:8000 --name faassubmgr -e "SPECUIMDBCONNSTR=${SPECUIMDBCONNSTR}" --restart unless-stopped graboskyc/faassubmgr:latest

    echo
    echo "+================================"
    echo "| END:  FaasSubMgr"
    echo "+================================"
    echo
else
    echo
    echo "+================================"
    echo "| ERROR: Build failed"
    echo "+================================"
    echo
fi