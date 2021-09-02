#################################################
# WahBaby - PGSparkLite Plugin for Spark 40 Amp #
# Uses GuitarEQ6 setting to emulate Wah Pedal   #
#################################################

from lib.plugins.base import Plugin


class WahBaby(Plugin):

    _steps = {
        0:    (0.5, 1,   0.5, 0.1),
        0.1:  (0.4, 0.9, 0.6, 0.1),
        0.2:  (0.3, 0.8, 0.7, 0.2),
        0.3:  (0.2, 0.7, 0.8, 0.3),
        0.45: (0.1, 0.6, 0.9, 0.4),
        0.5:  (0.1, 0.5, 1,   0.5),
        0.55: (0.1, 0.5, 1,   0.5),
        0.6:  (0.1, 0.5, 1,   0.5),
        0.65: (0.1, 0.4, 0.9, 0.6),
        0.7:  (0.1, 0.3, 0.8, 0.7),
        0.8:  (0.1, 0.2, 0.6, 0.8),
        0.9:  (0.1, 0.1, 0.5, 0.9),
        1:    (0.1, 0.1, 0.5, 1)
    }

    def __init__(self, effect_name, type, enabled, params=None):
        super().__init__(effect_name, type, enabled)

        self._low_param = 2
        self._low_mid_param = 3
        self._mid_param = 4
        self._high_mid_param = 5        

    def calculate_params(self, value):
        step = self._steps[min(
            self._steps.keys(), key=lambda key: abs(key-value))]
        return [(self._low_param, step[0]), (self._low_mid_param, step[1]), (self._mid_param, step[2]), (self._high_mid_param, step[3])]
