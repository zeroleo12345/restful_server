#!/usr/bin/env bash

if [[ "$DEBUG" == "True" || "$DEBUG" == "1" ]]; then
    sleep 360
else
    exec python manage.py manage_order
fi
