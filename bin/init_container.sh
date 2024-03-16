#!/bin/sh
set -e

if [ "$ENVIROMENT" = "dev" ]; then
    make app-start-debug
else
    make app-start
fi