#!/usr/bin/env sh
set -o verbose

docker-compose exec web ../.test/runtest

# docker-compose exec web pytest  trade/user/tests.py
# docker-compose exec web pytest  -k  test_payjs_post
