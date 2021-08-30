######################################################
# Volume Pedal - PGSparkLite Plugin for Spark 40 Amp #
# Uses Master volume setting to emulate Volume Pedal #
######################################################

from lib.plugins.base import Plugin

class VolumePedal(Plugin):        

    def __init__(self, effect_name, type, enabled, params):
        super().__init__(effect_name, type, enabled)
        
        self._rate = 0.05
        self._master_param = 4
        self._volume = params[0]

    def calculate_params(self, value):        
        self._volume = value
        return [(self._master_param,self._volume)]