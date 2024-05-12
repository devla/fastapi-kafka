#!/bin/bash

# Run server
gunicorn src.main:app --bind 0.0.0.0:8000 --workers 17 --worker-class uvicorn.workers.UvicornWorker --log-level debug
