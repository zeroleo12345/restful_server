#!/usr/bin/env sh
docker-compose exec web ../bin/runtox

# docker-compose exec web pytest trade/user/tests.py -k  test_user

