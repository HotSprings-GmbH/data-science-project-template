#!/bin/bash
cd "$(dirname "$0")/.."

dockerContainersRunning=$(docker ps -q | xargs)

if [[ -n $dockerContainersRunning ]]
    then
        echo "Some docker containers seem to be running. Stop them first."
        echo "Aborting"
        exit 1
fi

echo "No docker containers running. Cleaning './volumes/'"
rm -rf ./volumes/*
