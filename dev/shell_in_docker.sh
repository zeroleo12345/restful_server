#!/usr/bin/env sh
set -o verbose

docker-compose exec web python manage.py shell 

