import threading
from ast import literal_eval

from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO, emit

from lib.sparkdevices import SparkDevices
from lib.sparkampserver import SparkAmpServer

from EventNotifier import Notifier

#####################
# Application Setup
#####################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sparksrock'

config = None

socketio = SocketIO(app)

amp = SparkAmpServer(socketio)

##################
# Flask Routes
##################

@app.route('/changeeffect', methods=['POST'])
def change_effect():
    
    old_effect = request.form['oldeffect']
    new_effect = request.form['neweffect']
    effect_type = request.form['effecttype']
    log_change_only = request.form['logchangeonly']

    if log_change_only == 'false':
        if old_effect.isdigit():
            # Changing Reverb just requires change of value on parameter 6
            amp.change_effect_parameter('bias.reverb', 6,
                                        float('0.' + new_effect))
        else:
            amp.change_effect(amp.get_amp_effect_name(old_effect),
                              amp.get_amp_effect_name(new_effect))

        # Prevent loop when changing amp remotely and receiving update from amp
        amp.config.last_call = 'change_effect'

    amp.config.update_config(old_effect, 'change_effect', new_effect)

    current_effect = None
    effect_list = None

    if effect_type == 'COMP':
        current_effect = amp.config.comp
        effect_list = amp.config.comps
    elif effect_type == 'DRIVE':
        current_effect = amp.config.drive
        effect_list = amp.config.drives
    elif effect_type == 'AMP':
        current_effect = amp.config.amp
        effect_list = amp.config.amps
    elif effect_type == 'MODULATION':
        current_effect = amp.config.modulation
        effect_list = amp.config.modulations
    elif effect_type == 'DELAY':
        current_effect = amp.config.delay
        effect_list = amp.config.delays
    elif effect_type == 'REVERB':
        current_effect = amp.config.reverb
        effect_list = amp.config.reverbs

    if current_effect == None:
        return 'error'

    return render_template('effect.html',
                           effect_type=effect_type,
                           effect=current_effect,
                           effect_list=effect_list,
                           selector=True)


@app.route('/changeeffectparameter', methods=['POST'])
def change_effect_parameter():

    effect = request.form['id']
    parameter = int(request.form['parameter'])
    value = float(request.form['value'])

    amp.change_effect_parameter(amp.get_amp_effect_name(effect), parameter, value)
    amp.config.update_config(effect, 'change_parameter', value, parameter)

    return 'ok'


@app.route('/changepreset', methods=['POST'])
def change_preset():

    preset = request.form['preset']

    amp.change_to_preset(int(preset))

    return 'ok'


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'GET':
        return render_template('connect.html')
    else:
        # Start a separate thread to connect to the amp, keep user posted via SocketIO
        socketio.emit('connection-message',
                      {'message': 'Attempting to connect...'})

        connection = threading.Thread(target=amp.connect, args=(), daemon=True)
        connection.start()

        return 'ok'


@app.route('/', methods=['GET'])
def index():
    if amp.connected == False:
        return redirect(url_for('connect'))    

    return render_template('main.html', config=amp.config)


@app.route('/eject', methods=['POST'])
def eject():    
    eject = request.form['eject']
    if eject == 'true':
        amp.config = None
        amp.eject()
        socketio.emit('connection-lost', {'url': url_for('connect')})

    return 'ok'


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/turneffectonoff', methods=['POST'])
def turn_effect_onoff():    
    effect = request.form['id']
    state = request.form['state']

    amp.turn_effect_onoff(amp.get_amp_effect_name(effect), state)

    amp.config.update_config(effect, 'turn_on_off', state)

    amp.config.last_call = 'turn_on_off'

    return 'ok'


if __name__ == '__main__':
    socketio.run(app)
