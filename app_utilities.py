import threading

from flask import render_template

from app import amp, socketio
from database.service import get_pedal_presets_by_effect_name
from lib.common import (dict_bias_reverb, dict_change_effect,
                        dict_change_parameter, dict_connection_message,
                        dict_message, dict_Name, dict_pedal_status,
                        dict_turn_on_off, get_amp_effect_name)
from lib.messages import msg_amp_connected, msg_attempting_connect

####################
# Utility Functions
####################


def do_connect():
    # Start a separate thread to connect to the amp, keep user posted via SocketIO
    socketio.emit(dict_connection_message,
                  {dict_message: msg_attempting_connect})

    connection = threading.Thread(target=amp.connect, args=(), daemon=True)
    connection.start()


def change_effect(old_effect, new_effect):
    if old_effect.isdigit():
        # Changing Reverb just requires change of value on parameter 6
        amp.change_effect_parameter(dict_bias_reverb, 6,
                                    float('0.' + new_effect))
    else:
        amp.change_effect(get_amp_effect_name(old_effect),
                          get_amp_effect_name(new_effect))

    # Prevent loop when changing amp remotely and receiving update from amp
    amp.config.last_call = dict_change_effect


def config_request():
    # Send the latest config to attached Pedal clients
    socketio.emit(dict_connection_message,
                  {dict_message: msg_amp_connected})
    socketio.emit(dict_pedal_status, amp.get_pedal_status())


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


def update_pedal_state(pedal_parameter):
    parameters = pedal_parameter.parameters()
    for parameter in range(len(parameters)):
        value = float(parameters[parameter])
        amp.change_effect_parameter(get_amp_effect_name(
            pedal_parameter.effect_name), parameter, value)
        amp.config.update_config(
            pedal_parameter.effect_name, dict_change_parameter, value, parameter)

    amp.turn_effect_onoff(get_amp_effect_name(
        pedal_parameter.effect_name), pedal_parameter.on_off)
    amp.config.update_config(pedal_parameter.effect_name,
                             dict_turn_on_off, pedal_parameter.on_off)
    amp.config.last_call = dict_turn_on_off
