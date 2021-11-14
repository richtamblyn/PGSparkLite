from engineio.payload import Payload
from flask import Flask
from flask_socketio import SocketIO
from lib.sparkampserver import SparkAmpServer

#####################
# Application Setup
#####################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sparksrock'

config = None

Payload.max_decode_packets = 150

socketio = SocketIO(app)

amp = SparkAmpServer(socketio)

from app_flask import *
from app_events import *
from app_utilities import *

if __name__ == '__main__':
    socketio.run(app)
