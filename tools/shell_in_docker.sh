#!/usr/bin/env sh
set -o verbose

docker-compose exec api python manage.py shell 

