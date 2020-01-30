#!/usr/bin/env bash

if [[ "$DEBUG" == "True" || "$DEBUG" == "1" ]]; then
    sleep 360
else
    exec python /app/src/manage.py statistics
fi
