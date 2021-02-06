#!/usr/bin/env sh

export ENVIRONMENT=production; export DEBUG=0; docker-compose up -d api
export ENVIRONMENT=production; export DEBUG=0; docker-compose up -d timer_processor
