#!/bin/sh

if [ "$DEBUG" == "True" ]; then
    python manage.py migrate
    python manage.py runserver 0.0.0.0:80
else
    python manage.py migrate
    gunicorn trade.wsgi --threads 4 -b :80 --access-logfile -
fi
