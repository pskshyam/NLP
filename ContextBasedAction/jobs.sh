#!/usr/bin/env bash
celery -A jobs.config worker -P eventlet --loglevel=info -c 1
