#####################################################
# Spark Devices Class
#
# Container for the current Spark Amp configuration
#####################################################

import glob
from ast import literal_eval
from collections import OrderedDict
from operator import getitem
import uuid

from lib.common import (dict_AC_Boost, dict_AC_Boost_safe, dict_amp,
                        dict_bias_noisegate, dict_bias_noisegate_safe,
                        dict_BPM, dict_change_effect, dict_change_parameter,
                        dict_change_pedal_preset, dict_comp, dict_db_id,
                        dict_delay, dict_drive, dict_effect, dict_gate,
                        dict_mod, dict_Name, dict_name, dict_Off, dict_On,
                        dict_OnOff, dict_parameters, dict_Parameters,
                        dict_Pedals, dict_preset_id, dict_Preset_Number,
                        dict_reverb, dict_show_hide_pedal,
                        dict_switch_parameter, dict_turn_on_off, dict_UUID,
                        dict_visible)


class SparkDevices:

    configDirs = ['config/effects/gate', 'config/amps', 'config/effects/comp',
                  'config/effects/mod', 'config/effects/drive', 'config/effects/delay', 'config/effects/reverb']

    def __init__(self, preset):
        self.last_call = ''

        self.reset_static()
        self.reset()
        self.load()
        self.parse_preset(preset)

    def get_parameters(self, effect):
        if effect in self.amps:
            return self.amps[effect][dict_parameters]
        elif effect in self.comps:
            return self.comps[effect][dict_parameters]
        elif effect in self.drives:
            return self.drives[effect][dict_parameters]
        elif effect in self.modulations:
            return self.modulations[effect][dict_parameters]
        elif effect in self.delays:
            return self.delays[effect][dict_parameters]
        elif effect in self.reverbs:
            return self.reverbs[effect][dict_parameters]
        elif effect in self.gates:
            return self.gates[effect][dict_parameters]

    def get_current_effect_by_type(self, type):
        if type == dict_gate:
            return self.gate
        elif type == dict_comp:
            return self.comp
        elif type == dict_drive:
            return self.drive
        elif type == dict_amp:
            return self.amp
        elif type == dict_mod:
            return self.modulation
        elif type == dict_delay:
            return self.delay
        elif type == dict_reverb:
            return self.reverb

    def get_effect_list_by_type(self, type):
        if type == dict_gate:
            return self.gates
        elif type == dict_comp:
            return self.comps
        elif type == dict_drive:
            return self.drives
        elif type == dict_amp:
            return self.amps
        elif type == dict_mod:
            return self.modulations
        elif type == dict_delay:
            return self.delays
        elif type == dict_reverb:
            return self.reverbs

    def get_type_by_effect_name(self, effect):        
        if effect in self.amps:
            return dict_amp
        elif effect in self.comps:
            return dict_comp
        elif effect in self.drives:
            return dict_drive
        elif effect in self.modulations:
            return dict_mod
        elif effect in self.delays:
            return dict_delay
        elif effect in self.reverbs:
            return dict_reverb
        elif effect in self.gates:
            return dict_gate

    def initialise_effect(self, effect_id, effect, onoff, parameters=None):
        effect[dict_Name] = effect_id
        effect[dict_OnOff] = onoff
        effect[dict_preset_id] = 0
        effect[dict_db_id] = 0
        effect[dict_visible] = True

        if parameters == None:
            effect[dict_Parameters] = []
            for parameter in effect[dict_parameters]:
                effect[dict_Parameters].append(0.5000)
        else:
            effect[dict_Parameters] = parameters

        return effect

    def initialise_chain_preset(self, name):
        self.chain_preset_id = 0
        self.presetName = name
        self.uuid = str(uuid.uuid4())
        
        if self.gate[dict_preset_id] == 0 or self.gate[dict_preset_id] == None:
            self.gate[dict_db_id] = 0

        if self.comp[dict_preset_id] == 0 or self.comp[dict_preset_id] == None:
            self.comp[dict_db_id] = 0

        if self.drive[dict_preset_id] == 0 or self.drive[dict_preset_id] == None:
            self.drive[dict_db_id] = 0

        if self.amp[dict_preset_id] == 0 or self.amp[dict_preset_id] == None:
            self.amp[dict_db_id] = 0

        if self.modulation[dict_preset_id] == 0 or self.modulation[dict_preset_id] == None:
            self.modulation[dict_db_id] = 0

        if self.delay[dict_preset_id] == 0 or self.delay[dict_preset_id] == None:
            self.delay[dict_db_id] = 0

        if self.reverb[dict_preset_id] == 0 or self.reverb[dict_preset_id] == None:
            self.reverb[dict_db_id] = 0

    def load(self):
        for configDir in self.configDirs:
            configFiles = glob.glob(configDir + '/*.json')

            for configFile in configFiles:
                with open(configFile, 'r') as f:
                    configObject = f.read()

                device = literal_eval(configObject)

                for id, values in device.items():
                    if values[dict_effect] == 'amp':
                        self.amps[id] = values
                    elif values[dict_effect] == 'gate':
                        self.gates[id] = values
                    elif values[dict_effect] == 'comp':
                        self.comps[id] = values
                    elif values[dict_effect] == 'drive':
                        self.drives[id] = values
                    elif values[dict_effect] == 'modulation':
                        self.modulations[id] = values
                    elif values[dict_effect] == 'delay':
                        self.delays[id] = values
                    elif values[dict_effect] == 'reverb':
                        self.reverbs[id] = values

        self.amps = OrderedDict(
            sorted(self.amps.items(), key=lambda x: getitem(x[1], dict_name)))
        self.comps = OrderedDict(
            sorted(self.comps.items(), key=lambda x: getitem(x[1], dict_name)))
        self.drives = OrderedDict(
            sorted(self.drives.items(), key=lambda x: getitem(x[1], dict_name)))
        self.modulations = OrderedDict(
            sorted(self.modulations.items(), key=lambda x: getitem(x[1], dict_name)))
        self.delays = OrderedDict(
            sorted(self.delays.items(), key=lambda x: getitem(x[1], dict_name)))
        self.reverbs = OrderedDict(
            sorted(self.reverbs.items(), key=lambda x: getitem(x[1], dict_name)))

    def parse_chain_preset(self, chain_preset):        
        self.gate[dict_Parameters] = chain_preset.gate_pedal.parameters()
        self.gate[dict_visible] = chain_preset.gate_pedal.visible
        self.gate[dict_OnOff] = chain_preset.gate_pedal.on_off
        self.gate[dict_db_id] = chain_preset.gate_pedal.id
        self.gate[dict_preset_id] = chain_preset.gate_pedal.pedal_preset_id

        self.comp[dict_Name] = chain_preset.comp_pedal.effect_name
        self.comp[dict_Parameters] = chain_preset.comp_pedal.parameters()
        self.comp[dict_visible] = chain_preset.comp_pedal.visible
        self.comp[dict_OnOff] = chain_preset.comp_pedal.on_off
        self.comp[dict_db_id] = chain_preset.comp_pedal.id
        self.comp[dict_preset_id] = chain_preset.comp_pedal.pedal_preset_id

        self.drive[dict_Name] = chain_preset.drive_pedal.effect_name
        self.drive[dict_Parameters] = chain_preset.drive_pedal.parameters()
        self.drive[dict_visible] = chain_preset.drive_pedal.visible
        self.drive[dict_OnOff] = chain_preset.drive_pedal.on_off
        self.drive[dict_db_id] = chain_preset.drive_pedal.id
        self.drive[dict_preset_id] = chain_preset.drive_pedal.pedal_preset_id

        self.amp[dict_Name] = chain_preset.amp_pedal.effect_name
        self.amp[dict_Parameters] = chain_preset.amp_pedal.parameters()
        self.amp[dict_visible] = chain_preset.amp_pedal.visible
        self.amp[dict_OnOff] = chain_preset.amp_pedal.on_off
        self.amp[dict_db_id] = chain_preset.amp_pedal.id
        self.amp[dict_preset_id] = chain_preset.amp_pedal.pedal_preset_id

        self.modulation[dict_Name] = chain_preset.mod_pedal.effect_name
        self.modulation[dict_Parameters] = chain_preset.mod_pedal.parameters()
        self.modulation[dict_visible] = chain_preset.mod_pedal.visible
        self.modulation[dict_OnOff] = chain_preset.mod_pedal.on_off
        self.modulation[dict_db_id] = chain_preset.mod_pedal.id
        self.modulation[dict_preset_id] = chain_preset.mod_pedal.pedal_preset_id

        self.delay[dict_Name] = chain_preset.delay_pedal.effect_name
        self.delay[dict_Parameters] = chain_preset.delay_pedal.parameters()
        self.delay[dict_visible] = chain_preset.delay_pedal.visible
        self.delay[dict_OnOff] = chain_preset.delay_pedal.on_off
        self.delay[dict_db_id] = chain_preset.delay_pedal.id
        self.delay[dict_preset_id] = chain_preset.delay_pedal.pedal_preset_id

        self.reverb[dict_Name] = chain_preset.reverb_pedal.effect_name
        self.reverb[dict_Parameters] = chain_preset.reverb_pedal.parameters()
        self.reverb[dict_visible] = chain_preset.reverb_pedal.visible
        self.reverb[dict_OnOff] = chain_preset.reverb_pedal.on_off
        self.reverb[dict_db_id] = chain_preset.reverb_pedal.id
        self.reverb[dict_preset_id] = chain_preset.reverb_pedal.pedal_preset_id

        self.chain_preset_id = chain_preset.id
        self.presetName = chain_preset.name

    def parse_preset(self, preset):
        self.presetName = preset[dict_Name]
        self.uuid = preset[dict_UUID]
        self.bpm = preset[dict_BPM]

        try:
            self.preset = preset[dict_Preset_Number]
        except:
            self.preset = None

        self.gate = preset[dict_Pedals][0]

        # Fix the gate ID with an underscore
        if self.gate[dict_Name] == dict_bias_noisegate:
            self.gate[dict_Name] = dict_bias_noisegate_safe

        self.comp = preset[dict_Pedals][1]
        self.drive = preset[dict_Pedals][2]
        self.amp = preset[dict_Pedals][3]

        # Fix the AC Boost ID with an underscore
        if self.amp[dict_Name] == dict_AC_Boost:
            self.amp[dict_Name] = dict_AC_Boost_safe

        self.modulation = preset[dict_Pedals][4]
        self.delay = preset[dict_Pedals][5]

        self.reverb = preset[dict_Pedals][6]
        self.reverb[dict_Name] = str(self.reverb[dict_Parameters][6])[-1]

        # Initialise database ids and visibility
        self.gate[dict_db_id] = 0
        self.gate[dict_visible] = True
        self.gate[dict_preset_id] = 0
        self.comp[dict_db_id] = 0
        self.comp[dict_visible] = True
        self.comp[dict_preset_id] = 0
        self.amp[dict_db_id] = 0
        self.amp[dict_visible] = True
        self.amp[dict_preset_id] = 0
        self.drive[dict_db_id] = 0
        self.drive[dict_visible] = True
        self.drive[dict_preset_id] = 0
        self.modulation[dict_db_id] = 0
        self.modulation[dict_visible] = True
        self.modulation[dict_preset_id] = 0
        self.delay[dict_db_id] = 0
        self.delay[dict_visible] = True
        self.delay[dict_preset_id] = 0
        self.reverb[dict_db_id] = 0
        self.reverb[dict_visible] = True
        self.reverb[dict_preset_id] = 0

    def reset_static(self):
        self.amps = {}
        self.gates = {}
        self.comps = {}
        self.drives = {}
        self.modulations = {}
        self.delays = {}
        self.reverbs = {}

    def reset(self):
        self.chain_preset_id = 0
        self.preset = 0
        self.presetName = ''
        self.gate = ''
        self.comp = ''
        self.drive = ''
        self.amp = ''
        self.modulation = ''
        self.delay = ''
        self.reverb = ''
        self.bpm = 0
        self.uuid = ''

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
            switch_parameter = self.modulations[effect][dict_switch_parameter]
            effect_type = dict_mod
        elif effect in self.delays:
            config_effect = self.delay
            switch_parameter = self.delays[effect][dict_switch_parameter]
            effect_type = dict_delay
        elif effect in self.reverbs:
            config_effect = self.reverb
            switch_parameter = self.reverbs[effect][dict_switch_parameter]
            effect_type = dict_reverb

        if switch_parameter != parameter:
            return None

        if config_effect[dict_OnOff] == dict_On and value == 0.0000:
            return (effect_type, dict_Off)

        if config_effect[dict_OnOff] == dict_Off and value > 0.0000:
            return (effect_type, dict_On)

    def update_config(self, effect, action, value, parameter=None):
        # Allows us to preserve unsaved config changes through browser refresh / change
        if action == dict_show_hide_pedal:
            if effect == dict_gate:
                self.gate[dict_visible] = value
            elif effect == dict_comp:
                self.comp[dict_visible] = value
            elif effect == dict_drive:
                self.drive[dict_visible] = value
            elif effect == dict_amp:
                self.amp[dict_visible] = value
            elif effect == dict_mod:
                self.modulation[dict_visible] = value
            elif effect == dict_delay:
                self.delay[dict_visible] = value
            elif effect == dict_reverb:
                self.reverb[dict_visible] = value
            return

        if action == dict_change_pedal_preset:
            # Value returned as a tuple
            if effect == dict_gate:
                self.gate[dict_preset_id] = value[0]
                self.gate[dict_db_id] = value[1]
            elif effect == dict_comp:
                self.comp[dict_preset_id] = value[0]
                self.comp[dict_db_id] = value[1]
            elif effect == dict_drive:
                self.drive[dict_preset_id] = value[0]
                self.drive[dict_db_id] = value[1]
            elif effect == dict_amp:
                self.amp[dict_preset_id] = value[0]
                self.amp[dict_db_id] = value[1]
            elif effect == dict_mod:
                self.modulation[dict_preset_id] = value[0]
                self.modulation[dict_db_id] = value[1]
            elif effect == dict_delay:
                self.delay[dict_preset_id] = value[0]
                self.delay[dict_db_id] = value[1]
            elif effect == dict_reverb:
                self.reverb[dict_preset_id] = value[0]
                self.reverb[dict_db_id] = value[1]
            return

        if action == dict_turn_on_off:
            if effect == self.gate[dict_Name]:
                self.gate[dict_OnOff] = value
            elif effect == self.comp[dict_Name]:
                self.comp[dict_OnOff] = value
            elif effect == self.drive[dict_Name]:
                self.drive[dict_OnOff] = value
            elif effect == self.amp[dict_Name]:
                self.amp[dict_OnOff] = value
            elif effect == self.modulation[dict_Name]:
                self.modulation[dict_OnOff] = value
            elif effect == self.delay[dict_Name]:
                self.delay[dict_OnOff] = value
            elif effect == self.reverb[dict_Name]:
                self.reverb[dict_OnOff] = value
            return

        if action == dict_change_effect:
            if value in self.comps:
                self.comp = self.initialise_effect(
                    value, self.comps[value], self.comp[dict_OnOff])
            elif value in self.drives:
                self.drive = self.initialise_effect(
                    value, self.drives[value], self.drive[dict_OnOff])
            elif value in self.amps:
                self.amp = self.initialise_effect(
                    value, self.amps[value], self.amp[dict_OnOff], self.amp[dict_Parameters])
            elif value in self.modulations:
                self.modulation = self.initialise_effect(
                    value, self.modulations[value], self.modulation[dict_OnOff])
            elif value in self.delays:
                self.delay = self.initialise_effect(
                    value, self.delays[value], self.delay[dict_OnOff])
            elif value in self.reverbs:
                self.reverb = self.initialise_effect(
                    value, self.reverbs[value], self.reverb[dict_OnOff], self.reverb[dict_Parameters])
            return

        if action == dict_change_parameter:
            if effect == self.gate[dict_Name]:
                self.gate[dict_Parameters][parameter] = value
            elif effect == self.comp[dict_Name]:
                self.comp[dict_Parameters][parameter] = value
            elif effect == self.drive[dict_Name]:
                self.drive[dict_Parameters][parameter] = value
            elif effect == self.amp[dict_Name]:
                self.amp[dict_Parameters][parameter] = value
            elif effect == self.modulation[dict_Name]:
                self.modulation[dict_Parameters][parameter] = value
            elif effect == self.delay[dict_Name]:
                self.delay[dict_Parameters][parameter] = value
            elif effect == self.reverb[dict_Name]:
                self.reverb[dict_Parameters][parameter] = value

    def update_chain_preset_database_ids(self, chainPreset):
        if chainPreset == None:
            return

        self.chain_preset_id = chainPreset.id        
        self.presetName = chainPreset.name
        self.gate[dict_db_id] = chainPreset.gate_pedal.id
        self.gate[dict_visible] = chainPreset.gate_pedal.visible
        self.comp[dict_db_id] = chainPreset.comp_pedal.id
        self.comp[dict_visible] = chainPreset.comp_pedal.visible
        self.drive[dict_db_id] = chainPreset.drive_pedal.id
        self.drive[dict_visible] = chainPreset.drive_pedal.visible
        self.amp[dict_db_id] = chainPreset.amp_pedal.id
        self.amp[dict_visible] = chainPreset.amp_pedal.visible
        self.modulation[dict_db_id] = chainPreset.mod_pedal.id
        self.modulation[dict_visible] = chainPreset.mod_pedal.visible
        self.delay[dict_db_id] = chainPreset.delay_pedal.id
        self.delay[dict_visible] = chainPreset.delay_pedal.visible
        self.reverb[dict_db_id] = chainPreset.reverb_pedal.id
        self.reverb[dict_visible] = chainPreset.reverb_pedal.visible
