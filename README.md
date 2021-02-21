# PGSparkLite - Web Interface for the Spark 40 Amp

## Overview

Utilising the amazing work of Paul Hamshere https://github.com/paulhamsh/Spark-Parser, Justin Nelson https://github.com/jrnelson90/tinderboxpedal and Yuriy Tsibizov https://github.com/ytsibizov/midibox, this is a Python based project that allows the user to send and receive configuration changes to and from a Positive Grid Spark 40 Amp (https://www.positivegrid.com/spark/) via a web browser.

![PGSparkLite Interface](https://richtamblyn.co.uk/wp-content/uploads/2021/02/StoreRecallPT.jpg)

Written using the Flask framework and SocketIO, the intended target for this code could be a cheap Raspberry Pi Zero W that can host the interface, allowing other networked computers remote control of the connected Spark. It can also be setup on a Windows PC and accessed locally.

The realistic knobs and switch controls are possible thanks to the awesome G200KG Input Knobs library - https://g200kg.github.io/input-knobs/

## User Instructions
Guides to setting up PGSparkLite can be found in the Wiki: 

* Raspberry Pi - https://github.com/richtamblyn/PGSparkLite/wiki/How-to-setup-a-Raspberry-Pi-Zero-W-and-PGSparkLite-from-scratch
* Windows 10 - https://github.com/richtamblyn/PGSparkLite/wiki/How-to-setup-PGSparkLite-on-Windows-10

## Development Environment
This project was developed on a Raspberry Pi 4 (4GB RAM version) using the awesome Microsoft Visual Studio Code IDE. Launch configuration is included within the repository to allow you to run and debug the project locally. 

### Dependencies
- Python 3.x
- Flask 1.0.2 
- Flask-SocketIO 5.0.1
- PySerial 3.4
- Python3-bluez

### External Dependencies
This project uses CDN servers to retrieve JQuery 3.5.1 and SocketIO 3.0.4 JavaScript libraries. If you wish to download the libraries separately to remove the requirement for an external internet connection, the references can then be modified in the /templates/layout.html file.

## Future Development Ideas
- Storage of modified Amp presets on the amp and also in re-callable format via the web interface
- Implement light-weight backend database (SQLite) to support storage of presets for individual pedals.
