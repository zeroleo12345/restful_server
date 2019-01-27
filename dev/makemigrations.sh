#!/usr/bin/env sh
docker-compose exec api  python manage.py makemigrations trade
