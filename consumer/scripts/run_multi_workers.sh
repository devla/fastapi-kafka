#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$(pwd)/src

uvicorn src.main:app --workers 4 --proxy-headers --host 0.0.0.0 --port 8000 --lifespan on
