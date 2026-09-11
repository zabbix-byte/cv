#!/bin/sh
set -e

if [ "$ENVIROMENT" = "dev" ]; then
    make app-start-debug
elif [ "$ENVIROMENT" = "pro" ] || [ "$ENVIROMENT" = "prod" ]; then
    sh bin/start.sh
else
    make app-start
fi
