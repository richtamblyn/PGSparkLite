#################################################
# WahBaby - PGSparkLite Plugin for Spark 40 Amp #
# Uses GuitarEQ6 setting to emulate Wah Pedal   #
#################################################

from lib.plugins.base import Plugin

class WahBaby(Plugin):
    
    def __init__(self, effect_name, type, enabled, params):
        super().__init__(effect_name, type, enabled)        

        self.rate = 0.05        
        
        self.low = 3
        self.mid = 4
        self.high = 5

    def calculate_params(self, increase):        
        if increase == True:
            #TODO: Work out the filter
            print('blah')
        else:
            #TODO: Work out the filter
            print('blah')

        return [(self.low,0),(self.mid,0),(self.high,0)]
    