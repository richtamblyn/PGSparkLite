from peewee import DoesNotExist
from database.model import database, PedalParameter, PedalPreset, ChainPreset


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
    preset.gate_pedal_parameter = create_update_pedalparameter(config.gate)
    preset.comp_pedal_parameter = create_update_pedalparameter(config.comp)
    preset.drive_pedal_parameter = create_update_pedalparameter(
        config.drive)
    preset.amp_pedal_parameter = create_update_pedalparameter(config.amp)
    preset.mod_pedal_parameter = create_update_pedalparameter(
        config.modulation)
    preset.delay_pedal_parameter = create_update_pedalparameter(
        config.delay)
    preset.reverb_pedal_parameter = create_update_pedalparameter(
        config.reverb)
    preset.save()


def create_update_pedalparameter(pedal):
    if pedal['db_id'] != 0:
        try:
            record = PedalParameter.get(PedalParameter.id == pedal['db_id'])
        except DoesNotExist:
            record = PedalParameter()
    else:
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

def create_update_pedalpreset(data):
    preset_id = int(data['preset_id'])

    if preset_id != 0:
        try:
            record = PedalPreset.get(PedalPreset.id == preset_id)
        except DoesNotExist:
            record = PedalPreset()
    else:
        record = PedalPreset()

    record.name = str(data['name'])
    record.effect_name = str(data['effect'])

    pedal = {}

    if preset_id != 0:
        pedal['db_id'] = record.pedal_parameter.id
    else:
        pedal['db_id'] = 0

    pedal['Name'] = record.effect_name
    pedal['OnOff'] = data['onoff']
    pedal['Parameters'] = data['parameters']

    record.pedal_parameter = create_update_pedalparameter(pedal)

    record.save()

    return record.id


def get_pedal_presets(config):

    presets = {}
        
    presets["GATE"] = PedalPreset.select().where(PedalPreset.effect_name == config.gate['Name'])     
    presets["COMP"] = PedalPreset.select().where(PedalPreset.effect_name == config.comp['Name'])
    presets["DRIVE"] = PedalPreset.select().where(PedalPreset.effect_name == config.drive['Name'])
    presets["AMP"] = PedalPreset.select().where(PedalPreset.effect_name == config.amp['Name'])
    presets["MOD"] = PedalPreset.select().where(PedalPreset.effect_name == config.modulation['Name'])
    presets["DELAY"] = PedalPreset.select().where(PedalPreset.effect_name == config.delay['Name'])
    presets["REVERB"] = PedalPreset.select().where(PedalPreset.effect_name == config.reverb['Name'])

    return presets

def get_pedal_preset_by_effect_name(name):
    return PedalPreset.select().where(PedalPreset.effect_name == name)

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
    
    update_pedalparameter(config.gate, preset.gate_pedal_parameter)    
    update_pedalparameter(config.comp, preset.comp_pedal_parameter)
    update_pedalparameter(config.drive, preset.drive_pedal_parameter)    
    update_pedalparameter(config.amp, preset.amp_pedal_parameter)    
    update_pedalparameter(config.modulation, preset.mod_pedal_parameter)
    update_pedalparameter(config.delay, preset.delay_pedal_parameter)
    update_pedalparameter(config.reverb, preset.reverb_pedal_parameter)    

def update_pedalparameter(pedal, pedal_parameter):

    changed = False

    if pedal['Name'] != pedal_parameter.effect_name:
        changed = True
        pedal_parameter.effect_name = pedal['Name']

    if pedal['OnOff'] == 'On' and pedal_parameter.on_off == False:
        changed = True
        pedal_parameter.on_off = True
    elif pedal['OnOff'] == 'Off' and pedal_parameter.on_off == True:
        changed = True
        pedal_parameter.on_off = False

    count = 0

    for x in pedal['Parameters']:

        if count == 0:
            if pedal_parameter.p1_value != x:
                changed = True
                pedal_parameter.p1_value = x
        elif count == 1:
            if pedal_parameter.p2_value != x:
                changed = True
                pedal_parameter.p2_value = x
        elif count == 2:
            if pedal_parameter.p3_value != x:
                changed = True
                pedal_parameter.p3_value = x
        elif count == 3:
            if pedal_parameter.p4_value != x:
                changed = True
                pedal_parameter.p4_value = x
        elif count == 4:
            if pedal_parameter.p5_value != x:
                changed = True
                pedal_parameter.p5_value = x
        elif count == 5:
            if pedal_parameter.p6_value != x:
                changed = True
                pedal_parameter.p6_value = x

        count += 1

    if changed == True:
        pedal_parameter.save()
