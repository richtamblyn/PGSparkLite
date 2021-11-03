######################################################
# Volume Pedal - PGSparkLite Plugin for Spark 40 Amp #
# Uses Master volume setting to emulate Volume Pedal #
######################################################

from lib.plugins.base import Plugin

class VolumePedal(Plugin):        

    def __init__(self, effect_name):
        super().__init__(effect_name, "param")                
        self._master_param = 4        

    def calculate_params(self, value):                
        return [(self._master_param, value)]