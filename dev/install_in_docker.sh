#!/usr/bin/env sh
set -o verbose

docker-compose exec web pip install -r ../requirements/test.txt

