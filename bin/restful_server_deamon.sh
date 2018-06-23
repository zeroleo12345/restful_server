#!/usr/bin/env sh

if [ "$DEBUG" == "True" ]; then
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000
else
    python manage.py migrate
    gunicorn trade.wsgi --threads 4 -b :8000 --access-logfile - --access-logformat '%(h)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(a)s" %(L)s'
fi
