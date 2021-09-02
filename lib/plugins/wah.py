#################################################
# WahBaby - PGSparkLite Plugin for Spark 40 Amp #
# Uses GuitarEQ6 setting to emulate Wah Pedal   #
#################################################

from lib.plugins.base import Plugin


class WahBaby(Plugin):

    _low_param = 2
    _low_mid_param = 3
    _mid_param = 4
    _high_mid_param = 5  

    _steps = {
        0:    [(_low_param, 0.5), (_low_mid_param, 1),   (_mid_param, 0.5)],
        0.1:  [(_low_param, 0.4), (_low_mid_param, 0.9), (_mid_param, 0.6), (_high_mid_param, 0.1)],
        0.2:  [(_low_param, 0.3), (_low_mid_param, 0.8), (_mid_param, 0.7), (_high_mid_param, 0.2)],
        0.3:  [(_low_param, 0.2), (_low_mid_param, 0.7), (_mid_param, 0.8), (_high_mid_param, 0.3)],
        0.4:  [(_low_param, 0.1), (_low_mid_param, 0.6), (_mid_param, 0.9), (_high_mid_param, 0.4)],        
        0.6:  [(_low_mid_param, 0.5), (_mid_param, 1),   (_high_mid_param, 0.5)],
        0.8:  [(_low_mid_param, 0.4), (_mid_param, 0.9), (_high_mid_param, 0.6)],
        0.85: [(_low_mid_param, 0.3), (_mid_param, 0.8), (_high_mid_param, 0.7)],
        0.9:  [(_low_mid_param, 0.2), (_mid_param, 0.6), (_high_mid_param, 0.8)],
        0.95: [(_low_mid_param, 0.1), (_mid_param, 0.5), (_high_mid_param, 0.9)],
        1:    [(_high_mid_param, 1)]
    }

    def __init__(self, effect_name, type, enabled, params=None):
        super().__init__(effect_name, type, enabled)              

    def calculate_params(self, value):
        step = self._steps[min(
            self._steps.keys(), key=lambda key: abs(key-value))]
        return step
