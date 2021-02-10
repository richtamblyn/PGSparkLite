#####################################################
# Spark Devices Class
#
# Container for the current Spark Amp configuration
#####################################################

import glob
from ast import literal_eval
from collections import OrderedDict 
from operator import getitem 

class SparkDevices:
    
    configDirs = ['config/effects/gate', 'config/amps', 'config/effects/comp',
    'config/effects/mod', 'config/effects/drive', 'config/effects/delay', 'config/effects/reverb']                   

    def __init__(self, preset):        
        
        # Dictionary helpers
        self.Name = 'Name'
        self.name = 'name'
        self.Pedals = 'Pedals'     
        self.OnOff = 'OnOff'  
        self.Parameters = 'Parameters'
        self.parameters = 'parameters'
        self.switch_parameter = 'switch_parameter'

        self.last_call = ''

        self.reset_static()
        self.reset()
        self.load()        
        self.parse_preset(preset)

    def switch_onoff_parameter(self, effect, parameter, value):
        
        switch_parameter = None
        config_effect = None
        
        if effect in self.amps:
            return None
        elif effect in self.comps:
            return None
        elif effect in self.drives:
            return None
        elif effect in self.modulations:
            config_effect = self.modulation
            switch_parameter = self.modulations[effect][self.switch_parameter]                        
        elif effect in self.delays:
            config_effect = self.delay
            switch_parameter = self.delays[effect][self.switch_parameter]
        elif effect in self.reverbs:
            config_effect = self.reverb
            switch_parameter = self.reverbs[effect][self.switch_parameter]

        if switch_parameter != parameter:
            return None

        if config_effect[self.OnOff] == 'On' and value == 0.0000:
            return 'Off'

        if config_effect[self.OnOff] == 'Off' and value > 0.0000:
            return 'On'

    def get_parameters(self, effect):
        if effect in self.amps:
            return self.amps[effect][self.parameters]
        elif effect in self.comps:
            return self.comps[effect][self.parameters]
        elif effect in self.drives:
            return self.drives[effect][self.parameters]
        elif effect in self.modulations:
            return self.modulations[effect][self.parameters]
        elif effect in self.delays:
            return self.delays[effect][self.parameters]
        elif effect in self.reverbs:
            return self.reverbs[effect][self.parameters]

    def reset_static(self):
        self.amps = {}
        self.gates = {}
        self.comps = {}
        self.drives = {}
        self.modulations = {}
        self.delays = {}
        self.reverbs = {}

    def reset(self):
        self.preset = 0
        self.presetName = ''
        self.gate = ''
        self.comp = ''
        self.drive = ''
        self.amp = ''
        self.modulation = ''
        self.delay = ''
        self.reverb = ''        

    def load(self):
        for configDir in self.configDirs:
            configFiles = glob.glob(configDir + '/*.json')    

            for configFile in configFiles:
                with open(configFile,'r') as f:
                    configObject = f.read()
                    
                device = literal_eval(configObject)

                for id, values in device.items():                        
                    if values['effect'] == 'amp':
                        self.amps[id] = values
                    elif values['effect'] == 'gate':
                        self.gates[id] = values
                    elif values['effect'] == 'comp':
                        self.comps[id] = values
                    elif values['effect'] == 'drive':
                        self.drives[id] = values
                    elif values['effect'] == 'modulation':
                        self.modulations[id] = values
                    elif values['effect'] == 'delay':
                        self.delays[id] = values
                    elif values['effect'] == 'reverb':
                        self.reverbs[id] = values
                
        self.amps = OrderedDict(sorted(self.amps.items(), key = lambda x: getitem(x[1], 'name'))) 
        self.comps = OrderedDict(sorted(self.comps.items(), key = lambda x: getitem(x[1], 'name'))) 
        self.drives = OrderedDict(sorted(self.drives.items(), key = lambda x: getitem(x[1], 'name'))) 
        self.modulations = OrderedDict(sorted(self.modulations.items(), key = lambda x: getitem(x[1], 'name'))) 
        self.delays = OrderedDict(sorted(self.delays.items(), key = lambda x: getitem(x[1], 'name'))) 
        self.reverbs = OrderedDict(sorted(self.reverbs.items(), key = lambda x: getitem(x[1], 'name'))) 

    def parse_preset(self, preset):             
        self.presetName = preset[self.Name]
        
        self.preset = preset['PresetNumber']
        self.gate = preset[self.Pedals][0]      

        # Fix the gate ID with an underscore
        if self.gate[self.Name] == 'bias.noisegate':
            self.gate[self.Name] = 'bias_noisegate'

        self.comp = preset[self.Pedals][1]
        self.drive = preset[self.Pedals][2]        
        self.amp = preset[self.Pedals][3]

        # Fix the AC Boost ID with an underscore
        if self.amp[self.Name] == 'AC Boost':
            self.amp[self.Name] = 'AC_Boost'

        self.modulation = preset[self.Pedals][4]
        self.delay = preset[self.Pedals][5]
                
        self.reverb = preset[self.Pedals][6]
        self.reverb[self.Name] = str(self.reverb[self.Parameters][6])[-1]

    def initialise_effect(self, effect_id, effect, onoff, parameters = None):
        effect[self.Name] = effect_id
        effect[self.OnOff] = onoff

        if parameters == None:
            effect[self.Parameters] = {}
            for parameter in effect[self.parameters]:
                effect[self.Parameters][parameter['id']] = 0.5
        else:
            effect[self.Parameters] = parameters
        
        return effect

    def update_config(self, effect, action, value, parameter = None):        
        # Allows us to preserve unsaved config changes through browser refresh / change
        if action == 'turn_on_off':
            if effect == self.gate[self.Name]:
                self.gate[self.OnOff] = value
            elif effect == self.comp[self.Name]:
                self.comp[self.OnOff] = value
            elif effect == self.drive[self.Name]:
                self.drive[self.OnOff] = value
            elif effect == self.amp[self.Name]:
                self.amp[self.OnOff] = value
            elif effect == self.modulation[self.Name]:
                self.modulation[self.OnOff] = value
            elif effect == self.delay[self.Name]:
                self.delay[self.OnOff] = value
            elif effect == self.reverb[self.Name]:
                self.reverb[self.OnOff] = value
            return
        
        if action == 'change_effect':            
            if value in self.comps:
                self.comp = self.initialise_effect(value, self.comps[value], self.comp[self.OnOff])                
            elif value in self.drives:
                self.drive = self.initialise_effect(value, self.drives[value], self.drive[self.OnOff])                
            elif value in self.amps:
                self.amp = self.initialise_effect(value, self.amps[value], self.amp[self.OnOff], self.amp[self.Parameters])
            elif value in self.modulations:
                self.modulation = self.initialise_effect(value, self.modulations[value], self.modulation[self.OnOff])                
            elif value in self.delays:
                self.delay = self.initialise_effect(value, self.delays[value], self.delay[self.OnOff])                
            elif value in self.reverbs:
                self.reverb = self.initialise_effect(value, self.reverbs[value], self.reverb[self.OnOff], self.reverb[self.Parameters])                
            return

        if action == 'change_parameter':
            if effect == self.gate[self.Name]:
                self.gate[self.Parameters][parameter] = value
            elif effect == self.comp[self.Name]:
                self.comp[self.Parameters][parameter] = value
            elif effect == self.drive[self.Name]:
                self.drive[self.Parameters][parameter] = value
            elif effect == self.amp[self.Name]:
                self.amp[self.Parameters][parameter] = value
            elif effect == self.modulation[self.Name]:
                self.modulation[self.Parameters][parameter] = value
            elif effect == self.delay[self.Name]:
                self.delay[self.Parameters][parameter] = value            
            elif effect == self.reverb[self.Name]:
                self.reverb[self.Parameters][parameter] = value