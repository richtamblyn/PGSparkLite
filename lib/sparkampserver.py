#####################################################
# Spark Amp Server Class
#
# Handles two-way communication with a Spark Amp
#
# Some code originally written by paulhamsh.
# See https://github.com/paulhamsh/Spark-Parser
#####################################################

import threading
import time
import requests
import bluetooth

from lib.external.SparkReaderClass import SparkReadMessage
from lib.external.SparkCommsClass import SparkComms
from lib.external.SparkClass import SparkMessage
from lib.sparklistener import SparkListener
from lib.sparkdevices import SparkDevices

from EventNotifier import Notifier


class SparkAmpServer:
    def __init__(self, socketio):
        self.socketio = socketio
        self.connected = False
        self.msg = SparkMessage()
        self.bt_sock = None
        self.comms = None
        self.config = None

        self.notifier = Notifier(
            ["callback", "connection_lost", "preset_corrupt"])
        self.notifier.subscribe("callback", self.callback_event)
        self.notifier.subscribe("connection_lost", self.connection_lost_event)
        self.notifier.subscribe("preset_corrupt", self.preset_corrupt_event)

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
                print("  {} - {}".format(addr, bt_name))
                if bt_name == "Spark 40 Audio":
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

            self.socketio.emit('connection-message',
                               {'message': 'Retrieving Amp configuration...'})
            self.initialise()

        except Exception as e:
            print(e)
            self.socketio.emit('connection-message',
                               {'message': 'Connection failed.'})

    def initialise(self):
        return self.change_to_preset(0)

    def eject(self):
        self.listener.stop()

        # Send a final request to the amp for the Listener thread to realise it has to stop listening
        self.request_preset(0)

        # Now close the Bluetooth connection and release the amp into the wild.
        self.bt_sock.close()

        self.connected = False

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
        if effect == 'bias_noisegate':
            effect = 'bias.noisegate'
        elif effect.isdigit():
            effect = 'bias.reverb'
        return effect

    def get_js_effect_name(self, effect):
        # Modify amp IDs to make them JS friendly
        if effect == 'AC Boost':
            effect = 'AC_Boost'
        elif effect == 'bias.reverb':
            effect = self.config.reverb['Name']

        return effect

    ##################
    # Event Handling
    ##################

    def callback_event(self, data):
        # Preset button changed
        if 'NewPreset' in data:
            preset = data['NewPreset']
            self.socketio.emit('update-preset', {'value': preset})
            self.request_preset(preset)
            return

        # Parse inbound preset changes
        if 'PresetNumber' in data:
            if self.config == None or self.config.preset != data[
                    'PresetNumber']:
                # Load the configuration
                self.config = SparkDevices(data)
                self.socketio.emit('connection-success', {'url': '/'})
                return
            else:
                return

        # Change of amp
        if 'OldEffect' in data:
            if self.config.last_call == 'change_effect':
                self.config.last_call = ''
                return

            old_effect = self.get_js_effect_name(data['OldEffect'])
            new_effect = self.get_js_effect_name(data['NewEffect'])

            self.socketio.emit(
                'update-effect', {
                    'old_effect': old_effect,
                    'effect_type': 'AMP',
                    'new_effect': new_effect
                })
            self.config.update_config(old_effect, 'change_effect', new_effect)
            return

        # Effect / Amp changes
        if 'Effect' in data:

            # Ignore call back after effect is turned off
            if self.config.last_call == 'turn_on_off':
                self.config.last_call = ''
                return

            effect = self.get_js_effect_name(data['Effect'])
            parameter = data['Parameter']
            value = data['Value']

            self.config.update_config(effect, 'change_parameter', value,
                                      parameter)
            self.socketio.emit('update-parameter', {
                'effect': effect,
                'parameter': parameter,
                'value': value
            })

            # Check if physical knob turn has activated/deactivated this effect
            state = self.config.switch_onoff_parameter(effect, parameter,
                                                       value)

            if state == None:
                return

            self.socketio.emit('update-onoff', {
                'effect': effect,
                'state': state
            })
            self.config.update_config(effect, 'turn_on_off', state)

    def connection_lost_event(self):
        self.connected = False
        self.socketio.emit('connection-lost', {'url': '/'})

    def preset_corrupt_event(self):
        self.connected = False
        message = (
            'Preset cannot be read correctly. '
            'To resolve this, manually change to the preset on the amp, set all dials to zero and store the preset.'
            'Power cycle the amp, restart PGSparkLite server and try again.')
        self.socketio.emit('connection-message', {'message': message})
