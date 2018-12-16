#!/usr/bin/env sh

if [ "$DEBUG" == "True" ]; then
    sleep 360
else
    exec python /app/src/manage.py statistics
fi
