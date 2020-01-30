#!/usr/bin/env sh
set -o verbose

docker-compose exec  api pytest  -k  $1
