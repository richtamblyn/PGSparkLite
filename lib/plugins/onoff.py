#####################################################################
# Switch Effect On/Off Plugin - PGSparkLite Plugin for Spark 40 Amp #
#####################################################################

from lib.plugins.base import Plugin

class OnOff(Plugin):        

    def __init__(self, effect_name, effect_type):
        super().__init__(effect_name, "onoff")    
        self.effect_type = effect_type                    

    def calculate_state(self, value):                
        if value < 1:
            return False
        else:
            return True        