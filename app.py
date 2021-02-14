import threading
import json

from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO

from lib.sparkampserver import SparkAmpServer
from database.service import database, get_system_preset_by_id, sync_system_preset, get_pedal_presets, \
    get_pedal_presets_by_effect_name, create_update_pedalpreset, get_pedal_preset_by_id


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


@app.before_request
def _db_connect():
    database.connect()


@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()


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

    return render_effect(effect_type, True)


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


@app.route('/changepedalpreset', methods=['POST'])
def change_pedal_preset():
    preset_id = int(request.form['preset_id'])
    effect_name = str(request.form['effect_name'])
    effect_type = str(request.form['effect_type'])

    preset = get_pedal_preset_by_id(preset_id)
    parameters = preset.pedal_parameter.parameters()

    # Send the changes to the amp
    for parameter in range(len(parameters)):
        value = float(parameters[str(parameter)])
        amp.change_effect_parameter(
            amp.get_amp_effect_name(effect_name), parameter, value)
        amp.config.update_config(
            effect_name, 'change_parameter', value, parameter)

    if preset.pedal_parameter.on_off:
        state = 'On'
    else:
        state = 'Off'

    amp.turn_effect_onoff(amp.get_amp_effect_name(effect_name), state)
    amp.config.update_config(effect_name, 'turn_on_off', state)
    amp.config.last_call = 'turn_on_off'
    amp.config.update_config(effect_type, 'change_pedal_preset', preset.id)

    # Update the UI
    selector = True
    if effect_name == 'bias_noisegate':
        selector = False

    return render_effect(effect_type, selector, preset_id)

@app.route('/deletepedalpreset', methods=['POST'])
def delete_pedal_preset():
    preset_id = int(request.form['preset_id'])
    preset = get_pedal_preset_by_id(preset_id)
    effect_name = preset.effect_name    
    preset.delete_instance()    
    return render_template('effect_footer.html',
                           effect_name=effect_name,
                           effect_type=str(request.form['effect_type']),
                           presets=get_pedal_presets_by_effect_name(
                               effect_name),
                           preset_selected=0)


@app.route('/', methods=['GET'])
def index():
    if amp.connected == False:
        return redirect(url_for('connect'))

    # Always check that our database matches the amp preset settings
    sync_system_preset(amp.config)

    # Now update database id references in the in-memory config
    amp.config.update_system_preset_database_ids(
        get_system_preset_by_id(amp.config.preset))

    # Populate chain preset dropdown
    # TODO

    # Populate pedal preset dropdowns
    pedal_presets = get_pedal_presets(amp.config)

    return render_template('main.html', config=amp.config, pedal_presets=pedal_presets)


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/updatepedalpreset', methods=['POST'])
def update_pedal_preset():
    effect_name = str(request.form['effect'])
    preset_id = int(request.form['preset_id'])

    preset_name = None
    if preset_id == 0:
        preset_name = str(request.form['name'])

    on_off = str(request.form['onoff'])
    parameters = json.loads(request.form['parameters'])

    id = create_update_pedalpreset(
        effect_name, preset_name, preset_id, on_off, parameters)

    return render_template('effect_footer.html',
                           effect_name=effect_name,
                           effect_type=str(request.form['effect_type']),
                           presets=get_pedal_presets_by_effect_name(
                               effect_name),
                           preset_selected=id)

###########################
# SocketIO EventListeners
###########################


@socketio.event
def change_effect_parameter(data):
    effect = str(data['effect'])
    parameter = int(data['parameter'])
    value = float(data['value'])

    amp.change_effect_parameter(amp.get_amp_effect_name(effect), parameter,
                                value)
    amp.config.update_config(effect, 'change_parameter', value, parameter)


@socketio.event
def change_preset(data):
    amp.change_to_preset(int(data['preset']))


@socketio.event
def eject():
    amp.config = None
    amp.eject()
    socketio.emit('connection-lost', {'url': url_for('connect')})


@socketio.event
def turn_effect_onoff(data):
    effect = str(data['effect'])
    state = data['state']

    amp.turn_effect_onoff(amp.get_amp_effect_name(effect), state)
    amp.config.update_config(effect, 'turn_on_off', state)
    amp.config.last_call = 'turn_on_off'


@socketio.event
def reset_config():
    amp.config.reset_static()
    amp.config.load()

####################
# Utility Functions
####################


def render_effect(effect_type, selector, preset_selected=0):
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
    elif effect_type == 'MOD':
        current_effect = amp.config.modulation
        effect_list = amp.config.modulations
    elif effect_type == 'DELAY':
        current_effect = amp.config.delay
        effect_list = amp.config.delays
    elif effect_type == 'REVERB':
        current_effect = amp.config.reverb
        effect_list = amp.config.reverbs
    elif effect_type == 'GATE':
        current_effect = amp.config.gate
        effect_list = amp.config.gates

    if current_effect == None:
        return 'error'

    presets = get_pedal_presets_by_effect_name(current_effect['Name'])

    return render_template('effect.html',
                           effect_type=effect_type,
                           effect=current_effect,
                           effect_list=effect_list,
                           selector=selector,
                           presets=presets,
                           preset_selected=preset_selected)


if __name__ == '__main__':
    socketio.run(app)
