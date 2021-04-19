#!/usr/bin/env bash

# crond job
cp /app/bin/crontab/root  /var/spool/cron/crontabs/root
chmod 600 /var/spool/cron/crontabs/root
service cron start

python src/manage.py migrate
if [[ "$DEBUG" == "True" || "$DEBUG" == "1" ]]; then
    exec python src/manage.py runserver 0.0.0.0:8000
else
    exec gunicorn wsgi --threads 4 -b :8000 --access-logfile - --access-logformat '%(h)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(a)s" %(L)s'
fi
