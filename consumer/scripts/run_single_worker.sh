#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$(pwd)/src

uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port 8000 --lifespan on --reload-dir "$(pwd)/src" --reload-exclude '$(pwd)/venv/*' --reload
