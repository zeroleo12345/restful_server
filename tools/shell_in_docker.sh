#!/usr/bin/env sh
set -o verbose

docker-compose exec api python src/manage.py shell 

