#!/bin/bash
set -e

echo "Installing system dependencies including pybluez..."

# Update package lists with proper permissions
sudo apt-get update

# Install system-level dependencies for pybluez and other requirements
sudo apt-get install -y \
    libbluetooth-dev \
    bluez \
    libdbus-1-dev \
    libglib2.0-dev

echo "System dependencies installation completed!"
