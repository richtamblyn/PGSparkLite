#!/usr/bin/env bash

# Adjust this directory depending on your install directory
cd /home/pi/PGSparkLite

export FLASK_APP=app.py
python3 -m flask run --host=0.0.0.0