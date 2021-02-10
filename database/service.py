from peewee import DoesNotExist
from database.model import database, PedalParameter, PedalPreset, ChainPreset

def need_seed(system_preset_id):           
    if ChainPreset.select().where(ChainPreset.system_preset_id == system_preset_id).count() > 0:
        return False
    
    return True        
    

def create_update_chainpreset(config):
    # TODO: Is this new or update?  
    preset = ChainPreset()
    preset.name = config.presetName
    preset.system_preset_id = config.preset
    preset.gate_pedal_parameter_id = create_update_pedalparameter(config.gate)
    preset.drive_pedal_parameter_id = create_update_pedalparameter(config.drive)
    preset.amp_pedal_parameter_id = create_update_pedalparameter(config.amp)
    preset.mod_pedal_parameter_id = create_update_pedalparameter(config.modulation)
    preset.delay_pedal_parameter_id = create_update_pedalparameter(config.delay)
    preset.reverb_pedal_parameter_id = create_update_pedalparameter(config.reverb)
    preset.save() 


def create_update_pedalparameter(pedal):
    # TODO: Is this new or update?

    record = PedalParameter()
    record.effect_name = pedal['Name']
    
    if pedal['OnOff'] == 'On':
        record.on_off = True
    else:
        record.on_off = False

    count = 0

    for x in pedal['Parameters']:

        if count == 0:
            record.p1_value = x
        elif count == 1:
            record.p2_value = x
        elif count == 2:
            record.p3_value = x
        elif count == 3:
            record.p4_value = x
        elif count == 4:
            record.p5_value = x
        elif count == 5:
            record.p6_value = x

        count += 1
    
    record.save()

    return record.id