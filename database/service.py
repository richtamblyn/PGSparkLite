from lib.common import (dict_amp, dict_comp, dict_db_id, dict_delay,
                        dict_drive, dict_gate, dict_mod, dict_Name, dict_Off,
                        dict_On, dict_OnOff, dict_Parameters, dict_reverb,
                        dict_visible)
from peewee import DoesNotExist

from database.model import ChainPreset, PedalParameter, PedalPreset, database


def create_update_chainpreset(config):
    if config.chain_preset_id != 0:
        try:
            preset = ChainPreset.get(ChainPreset.id == config.chain_preset_id)
        except DoesNotExist:
            preset = ChainPreset()
    else:
        preset = ChainPreset()

    preset.name = config.presetName
    preset.system_preset_id = config.preset
    preset.uuid = config.uuid
    preset.bpm = config.bpm
    preset.gate_pedal = create_update_pedalparameter(config.gate)
    preset.comp_pedal = create_update_pedalparameter(config.comp)
    preset.drive_pedal = create_update_pedalparameter(
        config.drive)
    preset.amp_pedal = create_update_pedalparameter(config.amp)
    preset.mod_pedal = create_update_pedalparameter(
        config.modulation)
    preset.delay_pedal = create_update_pedalparameter(
        config.delay)
    preset.reverb_pedal = create_update_pedalparameter(
        config.reverb)
    preset.save()

    return preset.id


def create_update_pedalparameter(pedal):
    if pedal[dict_db_id] != 0:
        try:
            record = PedalParameter.get(PedalParameter.id == pedal[dict_db_id])
        except DoesNotExist:
            record = PedalParameter()
    else:
        record = PedalParameter()

    record.effect_name = pedal[dict_Name]
    record.on_off = pedal[dict_OnOff]
    record.store_parameters(pedal[dict_Parameters])
    record.visible = pedal[dict_visible]
    record.save()

    return record.id


def create_update_pedalpreset(preset_name, preset_id, effect):    
    try:
        record = PedalPreset.get(PedalPreset.id == preset_id)
    except DoesNotExist:
        # This is a new preset, create a new PedalParameter too
        record = PedalPreset()
        record.name = preset_name
        effect[dict_db_id] = 0
    
    record.effect_name = effect[dict_Name]    
    record.pedal_parameter = create_update_pedalparameter(effect)
    record.save()

    return record.id


def get_chain_presets():
    return ChainPreset.select().where(ChainPreset.system_preset_id == None)


def get_chain_preset_by_id(id):
    try:
        preset = ChainPreset.get(ChainPreset.id == id)
        return preset
    except DoesNotExist:
        return None


def get_pedal_presets(config):
    presets = {}

    presets[dict_gate] = get_pedal_presets_by_effect_name(
        config.gate[dict_Name])
    presets[dict_comp] = get_pedal_presets_by_effect_name(
        config.comp[dict_Name])
    presets[dict_drive] = get_pedal_presets_by_effect_name(
        config.drive[dict_Name])
    presets[dict_amp] = get_pedal_presets_by_effect_name(config.amp[dict_Name])
    presets[dict_mod] = get_pedal_presets_by_effect_name(
        config.modulation[dict_Name])
    presets[dict_delay] = get_pedal_presets_by_effect_name(
        config.delay[dict_Name])
    presets[dict_reverb] = get_pedal_presets_by_effect_name(
        config.reverb[dict_Name])

    return presets


def get_pedal_presets_by_effect_name(name):
    return (PedalPreset.select().where(PedalPreset.effect_name == name).order_by(+PedalPreset.effect_name))


def get_pedal_preset_by_id(id):
    try:
        return PedalPreset.get(PedalPreset.id == id)
    except DoesNotExist:
        return None


def get_system_preset_by_id(id):
    try:
        return ChainPreset.get(ChainPreset.system_preset_id == id)
    except DoesNotExist:
        return None


def sync_system_preset(config):
    preset = get_system_preset_by_id(config.preset)

    if preset == None:
        # Couldn't find a record for this preset, create a new one
        create_update_chainpreset(config)
        return

    update_pedalparameter(config.gate, preset.gate_pedal)
    update_pedalparameter(config.comp, preset.comp_pedal)
    update_pedalparameter(config.drive, preset.drive_pedal)
    update_pedalparameter(config.amp, preset.amp_pedal)
    update_pedalparameter(config.modulation, preset.mod_pedal)
    update_pedalparameter(config.delay, preset.delay_pedal)
    update_pedalparameter(config.reverb, preset.reverb_pedal)


def update_pedalparameter(pedal, pedal_parameter):
    changed = False

    if pedal[dict_Name] != pedal_parameter.effect_name:
        changed = True
        pedal_parameter.effect_name = pedal[dict_Name]

    if pedal[dict_OnOff] != pedal_parameter.on_off:
        changed = True
        pedal_parameter.on_off = pedal[dict_OnOff]
    
    if pedal[dict_visible] != pedal_parameter.visible:
        changed = True
        pedal_parameter.visible = pedal[dict_visible]

    count = 0

    params = pedal_parameter.parameters()

    for x in pedal[dict_Parameters]:
        if params[count] != x:
            changed = True
            params[count] = x

        count += 1

    if changed == True:
        pedal_parameter.store_parameters(params)
        pedal_parameter.save()
