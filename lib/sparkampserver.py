#####################################################
# Spark Amp Server Class
#
# Handles two-way communication with a Spark Amp
#
# Some code originally written by paulhamsh.
# See https://github.com/paulhamsh/Spark-Parser
#####################################################

import threading

import bluetooth
from EventNotifier import Notifier

from lib.common import (dict_AC_Boost, dict_AC_Boost_safe, dict_amp,
                        dict_bias_noisegate, dict_bias_noisegate_safe,
                        dict_bias_reverb, dict_callback, dict_chain_preset,
                        dict_change_effect, dict_connection_lost,
                        dict_connection_message, dict_effect, dict_Effect,
                        dict_effect_type, dict_log_change_only, dict_message,
                        dict_Name, dict_New_Effect, dict_new_effect,
                        dict_New_Preset, dict_Old_Effect, dict_old_effect,
                        dict_parameter, dict_Parameter, dict_preset_corrupt,
                        dict_Preset_Number, dict_state,
                        dict_turn_on_off, dict_value, dict_Value)
from lib.external.SparkClass import SparkMessage
from lib.external.SparkCommsClass import SparkComms
from lib.external.SparkReaderClass import SparkReadMessage
from lib.messages import (msg_connection_failed, msg_preset_error,
                          msg_retrieving_config)
from lib.sparkdevices import SparkDevices
from lib.sparklistener import SparkListener
from lib.sparkpreset import SparkPreset


class SparkAmpServer:
    def __init__(self, socketio):
        self.socketio = socketio
        self.connected = False
        self.msg = SparkMessage()
        self.bt_sock = None
        self.comms = None
        self.config = None

        self.notifier = Notifier(
            [dict_callback, dict_connection_lost, dict_preset_corrupt])
        self.notifier.subscribe(dict_callback, self.callback_event)
        self.notifier.subscribe(dict_connection_lost,
                                self.connection_lost_event)
        self.notifier.subscribe(dict_preset_corrupt, self.preset_corrupt_event)

        self.update_count = 0

    def change_to_preset(self, hw_preset):
        cmd = self.msg.change_hardware_preset(hw_preset)
        self.comms.send_it(cmd[0])
        self.request_preset(hw_preset)

    def change_effect(self, old_effect, new_effect):
        cmd = self.msg.change_effect(old_effect, new_effect)
        self.comms.send_it(cmd[0])

    def change_effect_parameter(self, effect, parameter, value):
        cmd = self.msg.change_effect_parameter(effect, parameter, value)
        self.comms.send_it(cmd[0])

    def connect(self):
        try:
            bt_devices = bluetooth.discover_devices(lookup_names=True)

            address = None

            for addr, bt_name in bt_devices:
                if bt_name == 'Spark 40 Audio':
                    address = addr

            self.bt_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.bt_sock.connect((address, 2))

            self.reader = SparkReadMessage()
            self.comms = SparkComms(self.bt_sock)

            # Start a separate thread to listen for control changes from the amp
            self.listener = SparkListener(self.reader, self.comms,
                                          self.notifier)

            t = threading.Thread(target=self.listener.start,
                                 args=(),
                                 daemon=True)
            t.start()

            self.connected = True

            self.socketio.emit(dict_connection_message,
                               {dict_message: msg_retrieving_config})
            self.initialise()

        except Exception as e:
            print(e)
            self.socketio.emit(dict_connection_message,
                               {dict_message: msg_connection_failed})

    def initialise(self):
        return self.change_to_preset(0)

    def eject(self):
        self.listener.stop()

        # Send a final request to the amp for the Listener thread to realise it has to stop listening
        self.request_preset(0)

        # Now close the Bluetooth connection and release the amp into the wild.
        self.bt_sock.close()

        self.connected = False

    def send_preset(self, chain_preset):
        chain_preset.preset = self.config.preset
        spark_preset = SparkPreset(chain_preset, type=dict_chain_preset)
        preset = self.msg.create_preset(spark_preset.json())

        for i in preset:
            self.bt_sock.send(i)

        change_user_preset = self.msg.change_hardware_preset(0x7f)

        self.bt_sock.send(change_user_preset[0])

        self.config.parse_chain_preset(chain_preset)

    def store_amp_preset(self):
        spark_preset = SparkPreset(self.config)
        preset = self.msg.create_preset(spark_preset.json())

        for i in preset:
            self.bt_sock.send(i)

        change_user_preset = self.msg.change_hardware_preset(
            self.config.preset)

        self.bt_sock.send(change_user_preset[self.config.preset])

    def turn_effect_onoff(self, effect, state):
        cmd = self.msg.turn_effect_onoff(effect, state)
        self.comms.send_it(cmd[0])

    def request_preset(self, hw_preset):
        self.comms.send_preset_request(hw_preset)

    ##################
    # Utility Methods
    ##################

    def get_amp_effect_name(self, effect):
        # Special cases to match internal amp ID
        if effect == dict_bias_noisegate_safe:
            effect = dict_bias_noisegate
        elif effect == dict_AC_Boost_safe:
            effect = dict_AC_Boost
        elif effect.isdigit():
            effect = dict_bias_reverb
        return effect

    def get_js_effect_name(self, effect):
        # Modify amp IDs to make them JS friendly
        if effect == dict_AC_Boost:
            effect = dict_AC_Boost_safe
        elif effect == dict_bias_reverb:
            effect = self.config.reverb[dict_Name]
        return effect

    ##################
    # Event Handling
    ##################

    def callback_event(self, data):
        # Preset button changed
        if dict_New_Preset in data:
            preset = data[dict_New_Preset]
            self.socketio.emit('update-preset', {dict_value: preset})
            self.request_preset(preset)
            return

        # Parse inbound preset changes
        if dict_Preset_Number in data:
            if self.config != None:
                # Check for updates we need to ignore
                cancel = False
                if self.config.last_call == dict_turn_on_off:
                    cancel = True
                elif self.config.last_call == dict_change_effect:
                    cancel = True
                elif self.config.last_call == dict_chain_preset:
                    self.update_count += 1
                    if self.update_count < 3:
                        return
                    cancel = True
                    self.update_count = 0

                if cancel == True:
                    self.config.last_call = ''
                    return

            if self.config == None or self.config.preset != data[
                    dict_Preset_Number]:

                self.config = SparkDevices(data)
                self.socketio.emit('connection-success', {'url': '/'})
                return
            else:
                self.update_count += 1
                if self.update_count == 3:
                    # User has stored preset on amp
                    self.socketio.emit(
                        'preset-stored', {dict_message: 'Preset was stored on Amp successfully.'})
                    self.update_count = 0
                return

        # Change of amp
        if dict_Old_Effect in data:
            if self.config.last_call == dict_change_effect:
                self.config.last_call = ''
                return

            old_effect = self.get_js_effect_name(data[dict_Old_Effect])
            new_effect = self.get_js_effect_name(data[dict_New_Effect])

            self.socketio.emit(
                'update-effect', {
                    dict_old_effect: old_effect,
                    dict_effect_type: dict_amp,
                    dict_new_effect: new_effect,
                    dict_log_change_only: False
                })
            self.config.update_config(
                old_effect, dict_change_effect, new_effect)
            return

        # Effect / Amp changes
        if dict_Effect in data:

            # Ignore call back after effect is turned off
            if self.config.last_call == dict_turn_on_off:
                self.config.last_call = ''
                return

            effect = self.get_js_effect_name(data[dict_Effect])
            parameter = data[dict_Parameter]
            value = data[dict_Value]

            self.config.update_config(effect, 'change_parameter', value,
                                      parameter)
            self.socketio.emit('update-parameter', {
                dict_effect: effect,
                dict_parameter: parameter,
                dict_value: value
            })

            # Check if physical knob turn has activated/deactivated this effect
            state = self.config.switch_onoff_parameter(effect, parameter,
                                                       value)

            if state == None:
                return

            self.socketio.emit('update-onoff', {
                dict_effect: effect,
                dict_state: state[1],
                dict_effect_type: state[0]
            })
            self.config.update_config(effect, dict_turn_on_off, state)

    def connection_lost_event(self):
        self.connected = False
        self.socketio.emit('connection-lost', {'url': '/'})

    def preset_corrupt_event(self):
        self.connected = False
        self.socketio.emit(dict_connection_message, {
                           dict_message: msg_preset_error})
