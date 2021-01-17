#####################################################
# Spark Amp Server Class
#
# Handles two-way communication with a Spark Amp
#
# Majority of code originally written by paulhamsh.
# See https://github.com/paulhamsh/Spark-Parser
#####################################################

import threading
import time
import requests
import bluetooth

from lib.external.SparkReaderClass import SparkReadMessage
from lib.external.SparkCommsClass import SparkComms
from lib.external.SparkClass import SparkMessage
from lib.sparklistener import listen
from lib.sparkdevices import SparkDevices

class SparkAmpServer:    

    def __init__(self, callback_url):        
        self.callback_url = callback_url
        self.connected = False
        self.msg = SparkMessage()
        self.bt_sock = None
        self.comms = None

    def change_effect(self, old_effect, new_effect):
        cmd = self.msg.change_effect(old_effect, new_effect)
        self.comms.send_it(cmd[0])
    
    def change_effect_parameter(self, effect, parameter, value):
        cmd = self.msg.change_effect_parameter(effect, parameter, value)
        self.comms.send_it(cmd[0])

    def change_to_preset(self, hw_preset):
        cmd = self.msg.change_hardware_preset(hw_preset)
        self.comms.send_it(cmd[0])        
        self.request_preset(hw_preset)

    def connect(self):        
        try:
            bt_devices = bluetooth.discover_devices(lookup_names=True)        

            for addr, bt_name in bt_devices:
                print("  {} - {}".format(addr, bt_name))
                if bt_name == "Spark 40 Audio":
                    address = addr

            self.bt_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.bt_sock.connect((address, 2))            
            
            self.reader = SparkReadMessage()
            self.comms = SparkComms(self.bt_sock)

            # Start a separate thread to listen for control changes from the amp
            self.listener = threading.Thread(target=listen, args=(self.reader, self.comms, self.callback_url), daemon=True)
            self.listener.start()                  

            self.connected = True      

            requests.post(self.callback_url, json = '{"Connected":True}')

        except:            
            requests.post(self.callback_url, json = '{"Connected":False}')

    def initialise(self):                        
        return self.change_to_preset(0)

    def eject(self):
        # Listener will resolve itself once it realises underlying connection has gone
        self.bt_sock.close()        
        self.connected = False

    def turn_effect_onoff(self, effect, state):
        cmd = self.msg.turn_effect_onoff(effect, state)
        self.comms.send_it(cmd[0])
    
    def request_preset(self, hw_preset):
        self.comms.send_preset_request(hw_preset)