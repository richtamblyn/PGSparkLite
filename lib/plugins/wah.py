#################################################
# WahBaby - PGSparkLite Plugin for Spark 40 Amp #
# Uses GuitarEQ6 setting to emulate Wah Pedal   #
#################################################

from lib.plugins.base import Plugin


class WahBaby(Plugin):

    _steps = {
        0: (0.75, 1, 0.75, 0.5, 0),
        0.05: (0.7, 0.95, 0.8, 0.55, 0),
        0.1: (0.65, 0.9, 0.85, 0.6, 0),
        0.15: (0.6, 0.85, 0.9, 0.65, 0),
        0.2: (0.55, 0.8, 0.95, 0.7, 0),
        0.25: (0.5, 0.75, 1, 0.75, 0),
        0.3: (0.5, 0.7, 0.95, 0.8, 0.5),
        0.35: (0.5, 0.65, 0.9, 0.85, 0.55),
        0.4: (0.5, 0.6, 0.85, 0.9, 0.6),
        0.45: (0.5, 0.55, 0.8, 0.95, 0.65),
        0.5: (0.5, 0.5, 0.75, 1, 0.7),
        0.55: (0.5, 0.5, 0.70, 0.95, 0.75),
        0.6: (0.5, 0.5, 0.65, 0.9, 0.8),
        0.65: (0.5, 0.5, 0.6, 0.85, 0.85),
        0.7: (0.5, 0.5, 0.55, 0.8, 0.9),
        0.75: (0.5, 0.5, 0.5, 0.75, 0.95),
        0.8: (0.5, 0.5, 0.5, 0.75, 1),
        0.85: (0.5, 0.5, 0.5, 0.8, 1),
        0.9: (0.5, 0.5, 0.55, 0.85, 1),
        0.95: (0.5, 0.5, 0.6, 0.9, 1),
        1: (0.5, 0.5, 0.65, 0.95, 1)
    }

    def __init__(self, effect_name, type, enabled, params=None):
        super().__init__(effect_name, type, enabled)

        self._low_param = 2
        self._low_mid_param = 3
        self._mid_param = 4
        self._high_mid_param = 5
        self._high_param = 6

    def calculate_params(self, value):        
        step = self._steps[min(
            self._steps.keys(), key=lambda key: abs(key-value))]
        return [(self._low_param, step[0]), (self._low_mid_param, step[1]), (self._mid_param, step[2]), (self._high_mid_param, step[3]), (self._high_param, step[4])]
