from flask import url_for

from app import amp, socketio
from app_utilities import config_request, do_connect
from lib.common import (dict_change_parameter, dict_change_preset,
                        dict_connect, dict_connection_lost, dict_effect,
                        dict_effect_type, dict_enabled, dict_parameter,
                        dict_preset, dict_preset_stored, dict_refresh_onoff,
                        dict_reload_client_interface, dict_show_hide_pedal,
                        dict_state, dict_turn_on_off, dict_url, dict_value,
                        dict_visible, get_amp_effect_name)

###########################
# SocketIO EventListeners
###########################


@socketio.event
def change_effect_parameter(data):
    effect = str(data[dict_effect])
    parameter = int(data[dict_parameter])
    value = float(data[dict_value])

    amp.change_effect_parameter(get_amp_effect_name(effect), parameter,
                                value)
    amp.config.update_config(effect, dict_change_parameter, value, parameter)


@socketio.event
def change_preset(data):
    amp.config.last_call = dict_change_preset
    amp.change_to_preset(int(data[dict_preset]))


@socketio.event
def eject():    
    amp.eject()
    socketio.emit(dict_connection_lost, {dict_url: url_for(dict_connect)})


@socketio.event
def expression_pedal(value):
    amp.expression_pedal(value)


@socketio.event
def pedal_connect(data):
    if amp.connected == False:
        do_connect()
    else:
        config_request()


@socketio.event
def pedal_config_request(data):
    config_request()


@socketio.event
def reload_interface(data):
    socketio.emit(dict_reload_client_interface, data)


@socketio.event
def reset_config():
    amp.config.reset_static()
    amp.config.load()


@socketio.event
def set_expression_param(data):        
    amp.update_plugin(data[dict_effect], data[dict_parameter], data[dict_enabled])


@socketio.event
def set_expression_onoff(data):        
    amp.update_plugin(data[dict_effect], None, data[dict_enabled], data[dict_effect_type])


@socketio.event
def show_hide_pedal(data):
    amp.config.update_config(
        data[dict_effect_type], dict_show_hide_pedal, data[dict_visible])


@socketio.event
def store_amp_preset():
    amp.config.last_call = dict_preset_stored
    amp.store_amp_preset()


@socketio.event
def toggle_effect_onoff(data):
    effect_type = data[dict_effect_type]
    result = amp.toggle_effect_onoff(effect_type)
    socketio.emit(dict_refresh_onoff, result)


@socketio.event
def turn_effect_onoff(data):
    effect = str(data[dict_effect])
    state = data[dict_state]

    amp.turn_effect_onoff(get_amp_effect_name(effect), state)
    amp.config.update_config(effect, dict_turn_on_off, state)
    amp.config.last_call = dict_turn_on_off
