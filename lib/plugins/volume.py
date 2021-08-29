######################################################
# Volume Pedal - PGSparkLite Plugin for Spark 40 Amp #
# Uses Master volume setting to emulate Volume Pedal #
######################################################

from lib.plugins.base import Plugin

class VolumePedal(Plugin):        

    def __init__(self, init_volume):
        super().__init__("volume","AMP", True)
        
        self._rate = 0.05
        self._master_param = 4
        self._volume = init_volume                                

    def calculate_params(self, increase):        
        if increase == True:
            self._volume += self.rate
            if self._volume > Plugin.max:
                self._volume = Plugin.max
        else:
            self._volume -= self.rate
            if self._volume < Plugin.min:
                self._volume = Plugin.min

        return ((self._master_param,self._volume))    