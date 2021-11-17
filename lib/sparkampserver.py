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

from lib.common import (dict_amp, dict_bias_reverb, dict_BPM, dict_bpm,
                        dict_bpm_change, dict_callback, dict_chain_preset,
                        dict_change_effect, dict_Change_Effect_State,
                        dict_change_parameter, dict_change_preset, dict_comp,
                        dict_connection_lost, dict_connection_message,
                        dict_connection_success, dict_delay, dict_drive,
                        dict_effect, dict_Effect, dict_effect_type, dict_gate,
                        dict_log_change_only, dict_message, dict_mod,
                        dict_Name, dict_name, dict_New_Effect, dict_new_effect,
                        dict_New_Preset, dict_Off, dict_Old_Effect,
                        dict_old_effect, dict_On, dict_OnOff, dict_parameter,
                        dict_Parameter, dict_pedal_chain_preset,
                        dict_pedal_status, dict_preset, dict_preset_corrupt,
                        dict_Preset_Number, dict_preset_stored,
                        dict_refresh_onoff, dict_reverb, dict_state,
                        dict_turn_on_off, dict_update_debug_log,
                        dict_update_effect, dict_update_onoff,
                        dict_update_parameter, dict_update_preset, dict_value,
                        dict_Value, get_amp_effect_name, get_js_effect_name)
from lib.external.SparkClass import SparkMessage
from lib.external.SparkCommsClass import SparkComms
from lib.external.SparkReaderClass import SparkReadMessage
from lib.messages import (msg_amp_connected, msg_amp_preset_stored,
                          msg_connection_failed, msg_preset_error,
                          msg_retrieving_config)
from lib.plugins.custom import CustomExpression
from lib.plugins.onoff import OnOff
from lib.plugins.volume import VolumePedal
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

        self.amp_update_count = 0
        self.chain_update_count = 0

        self.plugin = None

        self.debug_logging = False

        # Allow a user to disable the expression pedal temporarily via the web UI
        self.disable_expression_pedal = False

    def change_to_preset(self, hw_preset):
        cmd = self.msg.change_hardware_preset(hw_preset)
        success = self.comms.send_it(cmd[0])

        if not success:
            self.connection_lost_event()
        else:
            self.request_preset(hw_preset)

        self.log_debug_message("change_to_preset - value " + str(hw_preset))

    def change_effect(self, old_effect, new_effect):
        cmd = self.msg.change_effect(old_effect, new_effect)
        success = self.comms.send_it(cmd[0])

        if not success:
            self.connection_lost_event()

        self.log_debug_message("change_effect - old: " +
                               old_effect + " new: " + new_effect)

        # Have they unloaded effect that was controlled by expression?
        if self.plugin.name == old_effect:
            self.log_debug_message("change_effect - update_plugin")
            self.update_plugin(enabled=False)

    def change_effect_parameter(self, effect, parameter, value):
        cmd = self.msg.change_effect_parameter(effect, parameter, value)
        success = self.comms.send_it(cmd[0])

        if not success:
            self.connection_lost_event()

        self.log_debug_message("change parameter: effect: " + effect +
                               " parameter: " + str(parameter) + " value: " + str(value))

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

            self.socketio.emit(dict_connection_message,
                               {dict_message: msg_amp_connected})

        except Exception as e:
            print(e)
            self.socketio.emit(dict_connection_message,
                               {dict_message: msg_connection_failed})

    def log_debug_message(self, message):
        if self.debug_logging == True:
            self.socketio.emit(dict_update_debug_log,
                               {dict_message: message})

    def initialise(self):
        return self.comms.send_state_request()

    def eject(self):
        self.config = None
        self.listener.stop()

        # Send a final request to the amp for the Listener thread to realise it has to stop listening
        self.request_preset(0)

        # Now close the Bluetooth connection and release the amp into the wild.
        self.bt_sock.close()

        self.connected = False

    def expression_pedal(self, value):

        if self.disable_expression_pedal == True:
            self.log_debug_message(
                "expression_pedal - value received but is disabled")
            return

        self.log_debug_message(
            "expression_pedal - value received: " + str(value))

        if self.plugin.type == "param":

            self.log_debug_message("expression_pedal - plugin.type = param")

            params = self.plugin.calculate_params(value)
            if params == None:
                self.log_debug_message("expression_pedal - No params returned")
                return

            for param in params:
                self.change_effect_parameter(get_amp_effect_name(
                    self.plugin.name), param[0], param[1])

                self.socketio.emit(dict_update_parameter, {
                    dict_effect: self.plugin.name,
                    dict_parameter: param[0],
                    dict_value: param[1]
                })

            return

        if self.plugin.type == "onoff":
            self.log_debug_message("expression_pedal - plugin.type = onoff")
            isOn = self.plugin.calculate_state(value)
            if isOn:
                state = dict_On
                self.log_debug_message("expression_pedal - isOn = True")
            else:
                state = dict_Off
                self.log_debug_message("expression_pedal - isOn = False")

            self.socketio.emit(dict_update_onoff, {
                dict_state: state,
                dict_effect: self.plugin.name,
                dict_effect_type: self.plugin.effect_type
            })

            return

        self.log_debug_message("expression_pedal - plugin.type not found")

    def send_preset(self, chain_preset):
        self.log_debug_message("send_preset - " + chain_preset.name)

        chain_preset.preset = self.config.preset
        spark_preset = SparkPreset(chain_preset, type=dict_chain_preset)
        preset = self.msg.create_preset(spark_preset.json())

        for i in preset:
            self.bt_sock.send(i)

        change_user_preset = self.msg.change_hardware_preset(0x7f)

        self.bt_sock.send(change_user_preset[0])

        self.config.parse_chain_preset(chain_preset)

    def set_bpm(self, bpm):
        self.config.bpm = bpm
        spark_preset = SparkPreset(self.config, bpm=True)
        preset = self.msg.create_preset(spark_preset.json())

        for i in preset:
            self.bt_sock.send(i)

        change_user_preset = self.msg.change_hardware_preset(0x7f)

        self.bt_sock.send(change_user_preset[0])

        self.log_debug_message("set_bpm - value " + str(bpm))

    def store_amp_preset(self):
        spark_preset = SparkPreset(self.config)
        preset = self.msg.create_preset(spark_preset.json())

        for i in preset:
            self.bt_sock.send(i)

        change_user_preset = self.msg.change_hardware_preset(
            self.config.preset)

        self.bt_sock.send(change_user_preset[0])

    def toggle_effect_onoff(self, effect_type):
        effect = None
        effect_name = None

        # Ordered by priority for Pedal switching
        # Gate, comp and amp are optional hardware switches
        if effect_type == dict_drive:
            effect = self.config.drive
        elif effect_type == dict_mod:
            effect = self.config.modulation
        elif effect_type == dict_delay:
            effect = self.config.delay
        elif effect_type == dict_reverb:
            effect = self.config.reverb
            effect_name = self.config.reverb[dict_Name]
        elif effect_type == dict_gate:
            effect = self.config.gate
        elif effect_type == dict_comp:
            effect = self.config.comp
        elif effect_type == dict_amp:
            effect = self.config.amp

        if effect_name == None:
            get_js_effect_name(effect[dict_Name])

        state = dict_Off

        if effect[dict_OnOff] == dict_Off:
            state = dict_On

        self.turn_effect_onoff(
            get_amp_effect_name(effect[dict_Name]), state)

        self.config.update_config(effect[dict_Name], dict_turn_on_off, state)
        self.config.last_call = dict_turn_on_off

        self.log_debug_message(
            "toggle_effect_onoff - effect_type: " + effect_type + " state: " + state)

        return {dict_effect: effect_name,
                dict_state: state,
                dict_effect_type: effect_type}

    def turn_effect_onoff(self, effect, state):
        cmd = self.msg.turn_effect_onoff(effect, state)
        self.comms.send_it(cmd[0])

        self.log_debug_message(
            "turn_effect_onoff - effect: " + effect + " state: " + state)

    def request_preset(self, hw_preset):
        self.comms.send_preset_request(hw_preset)

    ##################
    # Utility Methods
    ##################

    def get_pedal_status(self):
        if self.config == None:
            return {}

        return {dict_drive: self.config.drive[dict_OnOff],
                dict_delay: self.config.delay[dict_OnOff],
                dict_mod: self.config.modulation[dict_OnOff],
                dict_reverb: self.config.reverb[dict_OnOff],
                dict_preset: self.config.preset,
                dict_BPM: str(int(self.config.bpm)),
                dict_Name: self.config.presetName,
                dict_chain_preset: self.config.chain_preset_id}

    def load_inbound_data(self, data):
        if self.config == None:
            self.config = SparkDevices(data)
        else:
            self.config.parse_preset(data)

        self.update_plugin()

        self.socketio.emit(dict_pedal_status, self.get_pedal_status())
        self.socketio.emit(dict_connection_success, {'url': '/'})

    def update_plugin(self, effect_name=None, param=None, enabled=None, effect_type=None):
        if effect_name == None or enabled == False:
            # Initialise Default Volume Pedal
            amp = self.config.get_current_effect_by_type(dict_amp)
            self.plugin = VolumePedal(amp[dict_Name])
        elif param == None:
            # Use the OnOff plugin for user selected effect
            self.plugin = OnOff(effect_name, effect_type)
        else:
            # Assign user selected effect and parameter
            self.plugin = CustomExpression(str(effect_name), param)

    ##################
    # Event Handling
    ##################

    def callback_event(self, data):
        # Preset button changed
        if dict_New_Preset in data:
            preset = data[dict_New_Preset]
            self.socketio.emit(dict_update_preset, {dict_value: preset})
            self.request_preset(preset)
            return

        # Parse inbound preset changes
        if dict_Preset_Number in data:
            if self.config != None and self.config.last_call != '':
                # Check for updates we need to ignore or notify on
                cancel = False
                if self.config.last_call == dict_turn_on_off:
                    cancel = True
                elif self.config.last_call == dict_change_effect:
                    cancel = True
                elif self.config.last_call == dict_chain_preset:
                    cancel = True
                elif self.config.last_call == dict_preset_stored:
                    self.socketio.emit(dict_preset_stored, {
                                       dict_message: msg_amp_preset_stored})
                    cancel = True
                elif self.config.last_call == dict_pedal_chain_preset or self.config.last_call == dict_change_preset:
                    self.load_inbound_data(data)
                    cancel = True

                if cancel == True:
                    self.config.last_call = ''
                    return

            if self.config == None or self.config.preset != data[
                    dict_Preset_Number]:
                self.load_inbound_data(data)
                return
            else:
                return

        # Change of amp
        if dict_Old_Effect in data:
            if self.config.last_call == dict_change_effect:
                self.config.last_call = ''
                return

            old_effect = get_js_effect_name(data[dict_Old_Effect])
            new_effect = get_js_effect_name(data[dict_New_Effect])

            self.socketio.emit(
                dict_update_effect, {
                    dict_old_effect: old_effect,
                    dict_effect_type: dict_amp,
                    dict_new_effect: new_effect,
                    dict_log_change_only: False
                })
            self.config.update_config(
                old_effect, dict_change_effect, new_effect)
            return

        # Mod / Delay knob changes to effect OnOff state
        if dict_Change_Effect_State in data:
            effect = data[dict_Change_Effect_State]
            effect_type = self.config.get_type_by_effect_name(effect)
            state = data[dict_OnOff]

            self.socketio.emit(dict_refresh_onoff, {
                dict_effect: effect,
                dict_state: state,
                dict_effect_type: effect_type
            })

            self.config.update_config(effect, dict_turn_on_off, state)

        # Effect / Amp changes
        if dict_Effect in data:

            # Ignore call back after effect is turned off
            if self.config.last_call == dict_turn_on_off:
                self.config.last_call = ''
                return

            if data[dict_Effect] == dict_bias_reverb:
                effect = self.config.reverb[dict_Name]
            else:
                effect = get_js_effect_name(data[dict_Effect])

            parameter = data[dict_Parameter]
            value = data[dict_Value]

            self.config.update_config(effect, dict_change_parameter, value,
                                      parameter)
            self.socketio.emit(dict_update_parameter, {
                dict_effect: effect,
                dict_parameter: parameter,
                dict_value: value
            })

            # Check if physical knob turn has activated/deactivated this effect
            state = self.config.switch_onoff_parameter(effect, parameter,
                                                       value)

            if state == None:
                return

            self.socketio.emit(dict_update_onoff, {
                dict_effect: effect,
                dict_state: state[1],
                dict_effect_type: state[0]
            })
            self.config.update_config(effect, dict_turn_on_off, state)

        # BPM change
        if dict_BPM in data:
            self.config.bpm = data[dict_BPM]
            self.socketio.emit(dict_bpm_change, {
                               dict_bpm: int(data[dict_BPM])})

    def connection_lost_event(self):
        self.connected = False
        self.socketio.emit('connection-lost', {'url': '/'})

    def preset_corrupt_event(self):
        self.connected = False
        self.socketio.emit(dict_connection_message, {
                           dict_message: msg_preset_error})
