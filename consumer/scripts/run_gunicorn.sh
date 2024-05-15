#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$(pwd)/src

gunicorn src.main:app --bind 0.0.0.0:8000 --workers 17 --worker-class uvicorn.workers.UvicornWorker
