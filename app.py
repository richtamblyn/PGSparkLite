import threading

from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO

from database.service import (create_update_chainpreset,
                              create_update_pedalpreset, database,
                              get_chain_preset_by_id, get_chain_presets,
                              get_pedal_preset_by_id, get_pedal_presets,
                              get_pedal_presets_by_effect_name,
                              get_system_preset_by_id, sync_system_preset,
                              verify_delete_chain_preset,
                              verify_delete_pedal_preset)
from lib.common import (dict_amp, dict_bias_noisegate_safe, dict_bias_reverb,
                        dict_change_effect, dict_change_parameter,
                        dict_change_pedal_preset, dict_comp,
                        dict_connection_lost, dict_connection_message,
                        dict_delay, dict_drive, dict_effect, dict_effect_type,
                        dict_gate, dict_log_change_only, dict_message,
                        dict_mod, dict_name, dict_Name, dict_new_effect,
                        dict_old_effect, dict_parameter, dict_preset,
                        dict_preset_id, dict_reverb, dict_show_hide_pedal,
                        dict_state, dict_turn_on_off, dict_value, dict_visible)
from lib.messages import msg_attempting_connect
from lib.sparkampserver import SparkAmpServer

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
    old_effect = request.form[dict_old_effect]
    new_effect = request.form[dict_new_effect]
    effect_type = request.form[dict_effect_type]
    log_change_only = request.form[dict_log_change_only]

    if log_change_only == 'false':
        change_effect(old_effect, new_effect)        

    amp.config.update_config(old_effect, dict_change_effect, new_effect)

    selector = True
    if new_effect == dict_bias_noisegate_safe:
        selector = False

    return render_effect(effect_type, selector)


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'GET':
        return render_template('connect.html')
    else:
        # Start a separate thread to connect to the amp, keep user posted via SocketIO
        socketio.emit(dict_connection_message,
                      {dict_message: msg_attempting_connect})

        connection = threading.Thread(target=amp.connect, args=(), daemon=True)
        connection.start()

        return 'ok'


@app.route('/changepedalpreset', methods=['POST'])
def change_pedal_preset():
    preset_id = int(request.form[dict_preset_id])    
    effect_type = str(request.form[dict_effect_type])

    preset = get_pedal_preset_by_id(preset_id)

    update_pedal_state(preset.pedal_parameter, effect_type)
    
    selector = True
    if preset.pedal_parameter.effect_name == dict_bias_noisegate_safe:
        selector = False

    return render_effect(effect_type, selector, preset_id)


@app.route('/deletechainpreset', methods=['POST'])
def delete_chain_preset():
    preset_id = int(request.form[dict_preset_id])
    if verify_delete_chain_preset(preset_id):
        chain_presets = get_chain_presets()
        return render_template('chain_preset_selector.html',
                           chain_presets=chain_presets,
                           preset_selected=0)

    return 'error'


@app.route('/deletepedalpreset', methods=['POST'])
def delete_pedal_preset():
    preset_id = int(request.form[dict_preset_id])
    preset = get_pedal_preset_by_id(preset_id)
    effect_name = preset.effect_name
    verify_delete_pedal_preset(preset_id)
    return render_template('effect_footer.html',
                           effect_name=effect_name,
                           effect_type=str(request.form[dict_effect_type]),
                           presets=get_pedal_presets_by_effect_name(
                               effect_name),
                           preset_selected=0)


@app.route('/effectfooter', methods=['POST'])
def effect_footer():    
    effect_name = request.form[dict_effect]    
    return render_template('effect_footer.html',
                            effect_name=effect_name,
                            effect_type=request.form[dict_effect_type],
                            presets=get_pedal_presets_by_effect_name(effect_name),
                            preset_selected = int(request.form[dict_preset_id]))


@app.route('/', methods=['GET','POST'])
def index():
    if amp.connected == False:
        return redirect(url_for('connect'))

    if request.method == 'GET':
        preset_id = 0
        
        sync_system_preset(amp.config)

        # Now update database id references in the in-memory config
        amp.config.update_chain_preset_database_ids(
            get_system_preset_by_id(amp.config.preset))
        
    else:
        preset_id = int(request.form[dict_preset_id])
        preset = get_chain_preset_by_id(preset_id)        
        amp.send_preset(preset)

        # TODO: Now update the amp config to render stuff

    return render_template('main.html',
                           config=amp.config,
                           pedal_presets=get_pedal_presets(amp.config),
                           chain_presets=get_chain_presets(),
                           preset_selected=preset_id)


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/updatechainpreset', methods=['POST'])
def update_chain_preset():
    preset_id = int(request.form[dict_preset_id])
    if preset_id == 0:
        amp.config.initialise_chain_preset(str(request.form[dict_name]))        

    id = create_update_chainpreset(amp.config)    
    chain_presets = get_chain_presets()

    preset = get_chain_preset_by_id(id)
    amp.config.update_chain_preset_database_ids(preset)

    return render_template('chain_preset_selector.html',
                           chain_presets=chain_presets,
                           preset_selected=id)


@app.route('/updatepedalpreset', methods=['POST'])
def update_pedal_preset():
    preset_id = int(request.form[dict_preset_id])
    effect_type = str(request.form[dict_effect_type])
    preset_name = None
    if preset_id == 0:
        preset_name = str(request.form[dict_name])

    effect = amp.config.get_current_effect_by_type(effect_type)

    id = create_update_pedalpreset(preset_name, preset_id, effect)
    amp.config.update_config(effect_type, dict_change_pedal_preset, id)

    return render_template('effect_footer.html',
                           effect_name=effect[dict_Name],
                           effect_type=effect_type,
                           presets=get_pedal_presets_by_effect_name(
                               effect[dict_Name]),
                           preset_selected=id)

###########################
# SocketIO EventListeners
###########################

@socketio.event
def change_chain_preset(data):
    preset_id = int(data[dict_preset_id])
    preset = get_chain_preset_by_id(preset_id)
    if preset == None:
        return

    amp.load_chain_preset(preset)
    socketio.emit('done-loading',{dict_state:True})


@socketio.event
def change_effect_parameter(data):
    effect = str(data[dict_effect])
    parameter = int(data[dict_parameter])
    value = float(data[dict_value])

    amp.change_effect_parameter(amp.get_amp_effect_name(effect), parameter,
                                value)
    amp.config.update_config(effect, dict_change_parameter, value, parameter)


@socketio.event
def change_preset(data):
    amp.change_to_preset(int(data[dict_preset]))


@socketio.event
def eject():
    amp.config = None
    amp.eject()
    socketio.emit(dict_connection_lost, {'url': url_for('connect')})


@socketio.event
def show_hide_pedal(data):
    amp.config.update_config(
        data[dict_effect_type], dict_show_hide_pedal, data[dict_visible])


@socketio.event
def turn_effect_onoff(data):
    effect = str(data[dict_effect])
    state = data[dict_state]

    amp.turn_effect_onoff(amp.get_amp_effect_name(effect), state)
    amp.config.update_config(effect, dict_turn_on_off, state)
    amp.config.last_call = dict_turn_on_off


@socketio.event
def reset_config():
    amp.config.reset_static()
    amp.config.load()

####################
# Utility Functions
####################

def change_effect(old_effect, new_effect):
    if old_effect.isdigit():
        # Changing Reverb just requires change of value on parameter 6
        amp.change_effect_parameter(dict_bias_reverb, 6,
                                    float('0.' + new_effect))
    else:
        amp.change_effect(amp.get_amp_effect_name(old_effect),
                            amp.get_amp_effect_name(new_effect))

    # Prevent loop when changing amp remotely and receiving update from amp
    amp.config.last_call = dict_change_effect


def render_effect(effect_type, selector, preset_selected=0):
    current_effect = amp.config.get_current_effect_by_type(
        effect_type)
    effect_list = amp.config.get_effect_list_by_type(effect_type)
    presets = get_pedal_presets_by_effect_name(current_effect[dict_Name])
    return render_template('effect.html',
                           effect_type=effect_type,
                           effect=current_effect,
                           effect_list=effect_list,
                           selector=selector,
                           presets=presets,
                           preset_selected=preset_selected)

def update_pedal_state(pedal_parameter, effect_type):
    parameters = pedal_parameter.parameters()
    for parameter in range(len(parameters)):
        value = float(parameters[parameter])
        amp.change_effect_parameter(amp.get_amp_effect_name(pedal_parameter.effect_name), parameter, value)
        amp.config.update_config(pedal_parameter.effect_name, dict_change_parameter, value, parameter)   

    amp.turn_effect_onoff(amp.get_amp_effect_name(pedal_parameter.effect_name), pedal_parameter.on_off)
    amp.config.update_config(pedal_parameter.effect_name, dict_turn_on_off, pedal_parameter.on_off)
    amp.config.last_call = dict_turn_on_off
    amp.config.update_config(effect_type, dict_change_pedal_preset, pedal_parameter.id)

if __name__ == '__main__':
    socketio.run(app)
