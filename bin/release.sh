#!/usr/bin/env sh

export ENVIRONMENT=production; export DEBUG=False; docker-compose up -d api
export ENVIRONMENT=production; export DEBUG=False; docker-compose up -d timer_processor
