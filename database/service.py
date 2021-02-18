from lib.common import (dict_amp, dict_comp, dict_db_id, dict_delay,
                        dict_drive, dict_gate, dict_mod, dict_Name, dict_OnOff,
                        dict_Parameters, dict_reverb, dict_visible)
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
    preset.gate_pedal = create_update_pedalparameter(config.gate, True)
    preset.comp_pedal = create_update_pedalparameter(config.comp, True)
    preset.drive_pedal = create_update_pedalparameter(config.drive, True)
    preset.amp_pedal = create_update_pedalparameter(config.amp, True)
    preset.mod_pedal = create_update_pedalparameter(config.modulation, True)
    preset.delay_pedal = create_update_pedalparameter(config.delay, True)
    preset.reverb_pedal = create_update_pedalparameter(config.reverb, True)
    preset.save()

    return preset.id


def create_update_pedalparameter(pedal, chain_preset=False):
    record = PedalParameter()

    if pedal[dict_db_id] != 0:
        try:
            record = PedalParameter.get(PedalParameter.id == pedal[dict_db_id])
            if chain_preset:
                if has_associated_system_preset(record.id) or has_associated_pedal_preset(record.id) and update_pedalparameter(pedal, record, False):
                    record = PedalParameter()
        except DoesNotExist:
            pass

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


def has_associated_system_preset(id):
    system_presets = ChainPreset.select().where(ChainPreset.system_preset_id != None)
    for preset in system_presets:
        if preset.gate_pedal.id == id:
            return True
        elif preset.comp_pedal.id == id:
            return True
        elif preset.drive_pedal.id == id:
            return True
        elif preset.amp_pedal.id == id:
            return True
        elif preset.mod_pedal.id == id:
            return True
        elif preset.delay_pedal.id == id:
            return True
        elif preset.reverb_pedal.id == id:
            return True

    return False


def has_associated_pedal_preset(id):
    if PedalPreset.select().where(PedalPreset.pedal_parameter == id).count() > 0:
        return True
    else:
        return False


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


def update_pedalparameter(pedal, pedal_parameter, apply_changes=True):
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
        try:
            if params[count] != x:
                changed = True
                params[count] = x

            count += 1
        except:
            print('Parameter count is incorrect for ' + pedal[dict_Name])

    if apply_changes and changed:
        pedal_parameter.store_parameters(params)
        pedal_parameter.save()

    return changed

def verify_delete_chain_preset(id):
    try:
        record = ChainPreset.get(ChainPreset.id == id)
    except DoesNotExist:
        return True

    if has_associated_pedal_preset(record.gate_pedal.id):
        pass
    else:
        record.gate_pedal.delete_instance()

    if has_associated_pedal_preset(record.comp_pedal.id):
        pass
    else:
        record.comp_pedal.delete_instance()

    if has_associated_pedal_preset(record.drive_pedal.id):
        pass
    else:
        record.drive_pedal.delete_instance()

    if has_associated_pedal_preset(record.amp_pedal.id):
        pass
    else:
        record.amp_pedal.delete_instance()

    if has_associated_pedal_preset(record.mod_pedal.id):
        pass
    else:
        record.mod_pedal.delete_instance()

    if has_associated_pedal_preset(record.delay_pedal.id):
        pass
    else:
        record.delay_pedal.delete_instance()

    if has_associated_pedal_preset(record.reverb_pedal.id):
        pass
    else:
        record.reverb_pedal.delete_instance()

    record.delete_instance()

    return True

