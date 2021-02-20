from lib.common import (dict_amp, dict_comp, dict_db_id, dict_delay,
                        dict_drive, dict_gate, dict_mod, dict_Name, dict_OnOff,
                        dict_Parameters, dict_reverb, dict_visible, dict_preset_id)
from peewee import DoesNotExist

from database.model import ChainPreset, PedalParameter, PedalPreset, database


def _cleanup_orphan_pedal(old_pedal, new_pedal):
    if old_pedal.is_system_preset:
        return
    elif old_pedal.pedal_preset_id == None and new_pedal[dict_preset_id] != None:
        old_pedal.delete_instance()


def create_update_chainpreset(config, system_preset=False):
    update = False

    if config.chain_preset_id != 0:
        try:
            preset = ChainPreset.get(ChainPreset.id == config.chain_preset_id)
            update = True
        except DoesNotExist:
            preset = ChainPreset()
    else:
        preset = ChainPreset()

    preset.name = config.presetName

    if system_preset:
        preset.system_preset_id = config.preset

    preset.uuid = config.uuid
    preset.bpm = config.bpm

    if update == True:
        _cleanup_orphan_pedal(preset.gate_pedal, config.gate)
        _cleanup_orphan_pedal(preset.comp_pedal, config.comp)
        _cleanup_orphan_pedal(preset.drive_pedal, config.drive)
        _cleanup_orphan_pedal(preset.amp_pedal, config.amp)
        _cleanup_orphan_pedal(preset.mod_pedal, config.modulation)
        _cleanup_orphan_pedal(preset.delay_pedal, config.delay)
        _cleanup_orphan_pedal(preset.reverb_pedal, config.reverb)

    preset.gate_pedal = create_update_pedalparameter(
        config.gate, chain_preset=True, system_preset=system_preset)

    preset.comp_pedal = create_update_pedalparameter(
        config.comp, chain_preset=True, system_preset=system_preset)

    preset.drive_pedal = create_update_pedalparameter(
        config.drive, chain_preset=True, system_preset=system_preset)

    preset.amp_pedal = create_update_pedalparameter(
        config.amp, chain_preset=True, system_preset=system_preset)

    preset.mod_pedal = create_update_pedalparameter(
        config.modulation, chain_preset=True, system_preset=system_preset)

    preset.delay_pedal = create_update_pedalparameter(
        config.delay, chain_preset=True, system_preset=system_preset)

    preset.reverb_pedal = create_update_pedalparameter(
        config.reverb, chain_preset=True, system_preset=system_preset)

    preset.save()

    return preset


def create_update_pedalparameter(pedal, chain_preset=False, system_preset=False):
    record = PedalParameter()
    record.is_system_preset = system_preset

    if pedal[dict_db_id] != 0:
        try:
            record = PedalParameter.get(PedalParameter.id == pedal[dict_db_id])
            if chain_preset:
                if record.is_system_preset or record.pedal_preset_id != None and update_pedalparameter(pedal, record, False):
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

    record.pedal_parameter.pedal_preset_id = record.id
    record.pedal_parameter.save()

    return record


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
        create_update_chainpreset(config, system_preset=True)
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

    if record.gate_pedal.pedal_preset_id == None:
        record.gate_pedal.delete_instance()

    if record.comp_pedal.pedal_preset_id == None:
        record.comp_pedal.delete_instance()

    if record.drive_pedal.pedal_preset_id == None:
        record.drive_pedal.delete_instance()

    if record.amp_pedal.pedal_preset_id == None:
        record.amp_pedal.delete_instance()

    if record.mod_pedal.pedal_preset_id == None:
        record.mod_pedal.delete_instance()

    if record.delay_pedal.pedal_preset_id == None:
        record.delay_pedal.delete_instance()

    if record.reverb_pedal.pedal_preset_id == None:
        record.reverb_pedal.delete_instance()

    record.delete_instance()

    return True


def verify_delete_pedal_preset(id):
    try:
        record = PedalPreset.get(PedalPreset.id == id)
    except DoesNotExist:
        return True

    gate_count = (PedalParameter
                  .select()
                  .join(ChainPreset, on=ChainPreset.gate_pedal)
                  .where(ChainPreset.gate_pedal.id == record.pedal_parameter.id)
                  .count())

    comp_count = (PedalParameter
                  .select()
                  .join(ChainPreset, on=ChainPreset.comp_pedal)
                  .where(ChainPreset.comp_pedal.id == record.pedal_parameter.id)
                  .count())

    drive_count = (PedalParameter
                   .select()
                   .join(ChainPreset, on=ChainPreset.drive_pedal)
                   .where(ChainPreset.drive_pedal.id == record.pedal_parameter.id)
                   .count())

    amp_count = (PedalParameter
                 .select()
                 .join(ChainPreset, on=ChainPreset.amp_pedal)
                 .where(ChainPreset.amp_pedal.id == record.pedal_parameter.id)
                 .count())

    mod_count = (PedalParameter
                 .select()
                 .join(ChainPreset, on=ChainPreset.mod_pedal)
                 .where(ChainPreset.mod_pedal.id == record.pedal_parameter.id)
                 .count())

    delay_count = (PedalParameter
                   .select()
                   .join(ChainPreset, on=ChainPreset.delay_pedal)
                   .where(ChainPreset.delay_pedal.id == record.pedal_parameter.id)
                   .count())

    reverb_count = (PedalParameter
                    .select()
                    .join(ChainPreset, on=ChainPreset.reverb_pedal)
                    .where(ChainPreset.reverb_pedal.id == record.pedal_parameter.id)
                    .count())

    if gate_count == 0 and comp_count == 0 and drive_count == 0 and amp_count == 0 and mod_count == 0 and delay_count == 0 and reverb_count == 0:
        record.pedal_parameter.delete_instance()
    else:
        record.pedal_parameter.pedal_preset_id = None
        record.pedal_parameter.save()

    record.delete_instance()

    return True
