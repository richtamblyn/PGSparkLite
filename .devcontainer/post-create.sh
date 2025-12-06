#!/bin/bash
set -e

echo "Creating Python virtual environment..."

# Create virtual environment
python -m venv venv

VENV_PIP="venv/bin/pip"
VENV_PYTHON="venv/bin/python"

echo "Upgrading pip and installing wheel..."

# Upgrade pip and install wheel
$VENV_PIP install --upgrade pip wheel setuptools

echo "Installing Python dependencies..."

# Install Python dependencies from requirements.txt
$VENV_PIP install -r requirements.txt

# Install pybluez from git (latest version with Python 3.9+ support)
$VENV_PIP install git+https://github.com/pybluez/pybluez.git#egg=pybluez

echo "Dev container setup completed successfully!"
