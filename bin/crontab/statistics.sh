#!/usr/bin/env bash

if [[ "$DEBUG" == "True" || "$DEBUG" == "1" ]]; then
    sleep 360
else
    exec /usr/local/bin/python /app/src/manage.py statistics
fi
