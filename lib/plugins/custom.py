###################################################################
# Custom Expression Control - PGSparkLite Plugin for Spark 40 Amp #
###################################################################

from lib.plugins.base import Plugin

class CustomExpression(Plugin):        

    def __init__(self, effect_name, param):
        super().__init__(effect_name, "param")                
        self._param = param        

    def calculate_params(self, value):                
        return [(self._param, value)]