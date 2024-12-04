#!/bin/bash

# Start cron daemon in the background
cron -f &
python3 index.py

# Run Flask app
python3 api.py