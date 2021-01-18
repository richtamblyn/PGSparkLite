#!/usr/bin/env bash

# Really simple startup script to expose PGSparkLite to external users
# Just make it executable and run it on startup
# Whilst this will probably meet most users requirements, I recommend using Supervisor for better resilience

# Adjust this directory depending on your install directory
cd /home/pi/PGSparkLite

export FLASK_APP=app.py
python3 -m flask run --host=0.0.0.0