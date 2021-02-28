from lib.common import (dict_bias_noisegate, dict_bias_reverb,
                        dict_chain_preset, dict_Name, dict_OnOff,
                        dict_Parameters)


class SparkPreset:
    def __init__(self, config, type=None):
        self.gate = {}
        self.comp = {}
        self.drive = {}
        self.amp = {}
        self.delay = {}
        self.mod = {}
        self.reverb = {}

        if type == dict_chain_preset:
            self._map_chain_preset_to_amp_preset(config)
        else:
            self._map_current_config_to_amp_preset(config)

    def _map_current_config_to_amp_preset(self, config):
        self.preset = config.preset
        self.uuid = config.uuid
        self.name = config.presetName
        self.bpm = config.bpm
        self.gate[dict_OnOff] = config.gate[dict_OnOff]
        self.gate[dict_Parameters] = config.gate[dict_Parameters]
        self.comp[dict_Name] = config.comp[dict_Name]
        self.comp[dict_OnOff] = config.comp[dict_OnOff]
        self.comp[dict_Parameters] = config.comp[dict_Parameters]
        self.drive[dict_Name] = config.drive[dict_Name]
        self.drive[dict_OnOff] = config.drive[dict_OnOff]
        self.drive[dict_Parameters] = config.drive[dict_Parameters]
        self.amp[dict_Name] = config.amp[dict_Name]
        self.amp[dict_OnOff] = config.amp[dict_OnOff]
        self.amp[dict_Parameters] = config.amp[dict_Parameters]
        self.mod[dict_Name] = config.modulation[dict_Name]
        self.mod[dict_OnOff] = config.modulation[dict_OnOff]
        self.mod[dict_Parameters] = config.modulation[dict_Parameters]
        self.delay[dict_Name] = config.delay[dict_Name]
        self.delay[dict_OnOff] = config.delay[dict_OnOff]
        self.delay[dict_Parameters] = config.delay[dict_Parameters]
        self.reverb[dict_OnOff] = config.reverb[dict_OnOff]
        self.reverb[dict_Parameters] = config.reverb[dict_Parameters]

    def _map_chain_preset_to_amp_preset(self, config):
        self.preset = config.preset
        self.uuid = config.uuid
        self.name = config.name
        self.bpm = config.bpm
        self.gate[dict_OnOff] = config.gate_pedal.on_off
        self.gate[dict_Parameters] = config.gate_pedal.parameters()
        self.comp[dict_Name] = config.comp_pedal.effect_name
        self.comp[dict_OnOff] = config.comp_pedal.on_off
        self.comp[dict_Parameters] = config.comp_pedal.parameters()
        self.drive[dict_Name] = config.drive_pedal.effect_name
        self.drive[dict_OnOff] = config.drive_pedal.on_off
        self.drive[dict_Parameters] = config.drive_pedal.parameters()
        self.amp[dict_Name] = config.amp_pedal.effect_name
        self.amp[dict_OnOff] = config.amp_pedal.on_off
        self.amp[dict_Parameters] = config.amp_pedal.parameters()
        self.mod[dict_Name] = config.mod_pedal.effect_name
        self.mod[dict_OnOff] = config.mod_pedal.on_off
        self.mod[dict_Parameters] = config.mod_pedal.parameters()
        self.delay[dict_Name] = config.delay_pedal.effect_name
        self.delay[dict_OnOff] = config.delay_pedal.on_off
        self.delay[dict_Parameters] = config.delay_pedal.parameters()
        self.reverb[dict_OnOff] = config.reverb_pedal.on_off
        self.reverb[dict_Parameters] = config.reverb_pedal.parameters()

    def json(self):
        return {"Preset Number": self.preset,
                "UUID": self.uuid,
                "Name": self.name,
                "Version": "0.7",
                "Description": self.name,
                "Icon": "icon.png",
                "BPM": self.bpm,
                "Pedals": [{dict_Name: dict_bias_noisegate,
                            dict_OnOff: self.gate[dict_OnOff],
                            dict_Parameters: self.gate[dict_Parameters]},
                           {dict_Name: self.comp[dict_Name],
                            dict_OnOff: self.comp[dict_OnOff],
                            dict_Parameters: self.comp[dict_Parameters]},
                           {dict_Name: self.drive[dict_Name],
                            dict_OnOff: self.drive[dict_OnOff],
                            dict_Parameters: self.drive[dict_Parameters]},
                           {dict_Name: self.amp[dict_Name],
                            dict_OnOff: self.amp[dict_OnOff],
                            dict_Parameters: self.amp[dict_Parameters]},
                           {dict_Name: self.mod[dict_Name],
                            dict_OnOff: self.mod[dict_OnOff],
                            dict_Parameters: self.mod[dict_Parameters]},
                           {dict_Name: self.delay[dict_Name],
                            dict_OnOff: self.delay[dict_OnOff],
                            dict_Parameters: self.delay[dict_Parameters]},
                           {dict_Name: dict_bias_reverb,
                            dict_OnOff: self.reverb[dict_OnOff],
                            dict_Parameters: self.reverb[dict_Parameters]}],
                "End Filler": 0xeb}
