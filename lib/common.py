# Dictionary helpers
dict_AC_Boost = 'AC Boost'
dict_AC_Boost_safe = 'AC_Boost'
dict_amp = 'AMP'
dict_bias_noisegate_safe = 'bias_noisegate'
dict_bias_noisegate = 'bias.noisegate'
dict_bias_reverb = 'bias.reverb'
dict_bpm = 'bpm'
dict_bpm_change = 'bpm-change'
dict_BPM = 'BPM'
dict_callback = 'callback'
dict_chain_preset = 'chain_preset'
dict_change_preset = 'change_preset'
dict_change_effect = 'change_effect'
dict_Change_Effect_State = 'ChangeEffectState'
dict_change_parameter = 'change_parameter'
dict_change_pedal_preset = 'change_pedal_preset'
dict_comp = 'COMP'
dict_connection_lost = 'connection_lost'
dict_connection_message = 'connection-message'
dict_connection_success = 'connection-success'
dict_db_id = 'db_id'
dict_delay = 'DELAY'
dict_drive = 'DRIVE'
dict_effect = 'effect'
dict_Effect = 'Effect'
dict_effect_name = 'effect_name'
dict_effect_type = 'effect_type'
dict_enabled = 'enabled'
dict_gate = 'GATE'
dict_GuitarEQ = 'GuitarEQ6'
dict_id = 'id'
dict_JH_Vox_846 = 'JH.Vox846'
dict_JH_Vox_846_Safe = 'JHVox846'
dict_JH_Dual_Showman = 'JH.DualShowman'
dict_JH_Dual_Showman_Safe = 'JHDualShowman'
dict_JH_Sunn_100 = 'JH.Sunn100'
dict_JH_Sunn_100_Safe = 'JHSunn100'
dict_JH_JTM45 = 'JH.JTM45'
dict_JH_JTM45_Safe = 'JHJTM45'
dict_JH_Bassman_Silver = 'JH.Bassman50Silver'
dict_JH_Bassman_Silver_Safe = 'JHBassman50Silver'
dict_JH_Super_Lead_100 = 'JH.SuperLead100'
dict_JH_Super_Lead_100_Safe = 'JHSuperLead100'
dict_JH_Sound_City_100 = 'JH.SoundCity100'
dict_JH_Sound_City_100_Safe = 'JHSoundCity100'
dict_JH_Axis_Fuzz = 'JH.AxisFuzz'
dict_JH_Axis_Fuzz_Safe = 'JHAxisFuzz'
dict_JH_Supa_Fuzz = 'JH.SupaFuzz'
dict_JH_Supa_Fuzz_Safe = 'JHSupaFuzz'
dict_JH_Octavia = 'JH.Octavia'
dict_JH_Octavia_Safe = 'JHOctavia'
dict_JH_Fuzz_Tone = 'JH.FuzzTone'
dict_JH_Fuzz_Tone_Safe = 'JHFuzzTone'
dict_JH_Voodoo_Vibe_Jr = 'JH.VoodooVibeJr'
dict_JH_Voodoo_Vibe_Jr_Safe = 'JHVoodooVibeJr'
dict_log_change_only = 'log_change_only'
dict_message = 'message'
dict_mod = 'MOD'
dict_Name = 'Name'
dict_name = 'name'
dict_New_Preset = 'NewPreset'
dict_new_effect = 'new_effect'
dict_New_Effect = 'NewEffect'
dict_Off = 'Off'
dict_old_effect = 'old_effect'
dict_Old_Effect = 'OldEffect'
dict_On = 'On'
dict_OnOff = 'OnOff'
dict_parameter = 'parameter'
dict_Parameter = 'Parameter'
dict_Parameters = 'Parameters'
dict_parameters = 'parameters'
dict_pedal_chain_preset = 'pedal_chain_preset'
dict_pedal_status = 'pedal-status'
dict_Pedals = 'Pedals'
dict_preset = 'preset'
dict_preset_corrupt = 'preset_corrupt'
dict_preset_id = 'preset_id'
dict_Preset_Number = 'PresetNumber'
dict_preset_stored = 'preset-stored'
dict_refresh_onoff = 'refresh-onoff'
dict_reload_client_interface = 'reload-client-interface'
dict_reverb = 'REVERB'
dict_show_hide_pedal = 'show_hide_pedal'
dict_state = 'state'
dict_switch_parameter = 'switch_parameter'
dict_turn_on_off = 'turn_on_off'
dict_update_effect = 'update-effect'
dict_update_onoff = 'update-onoff'
dict_update_parameter = 'update-parameter'
dict_update_preset = 'update-preset'
dict_UUID = 'UUID'
dict_value = 'value'
dict_Value = 'Value'
dict_visible = 'visible'

def get_amp_effect_name(effect):
    # Special cases to match internal amp ID
    if effect == dict_bias_noisegate_safe:
        effect = dict_bias_noisegate
    elif effect == dict_AC_Boost_safe:
        effect = dict_AC_Boost
    elif effect.isdigit():
        effect = dict_bias_reverb
    elif effect == dict_JH_Vox_846_Safe:
        effect = dict_JH_Vox_846
    elif effect == dict_JH_Dual_Showman_Safe:
        effect = dict_JH_Dual_Showman
    elif effect == dict_JH_Sunn_100_Safe:
        effect = dict_JH_Sunn_100
    elif effect == dict_JH_JTM45_Safe:
        effect = dict_JH_JTM45
    elif effect == dict_JH_Bassman_Silver_Safe:
        effect = dict_JH_Bassman_Silver
    elif effect == dict_JH_Super_Lead_100_Safe:
        effect = dict_JH_Super_Lead_100
    elif effect == dict_JH_Sound_City_100_Safe:
        effect = dict_JH_Sound_City_100
    elif effect == dict_JH_Axis_Fuzz_Safe:
        effect = dict_JH_Axis_Fuzz
    elif effect == dict_JH_Supa_Fuzz_Safe:
        effect = dict_JH_Supa_Fuzz
    elif effect == dict_JH_Octavia_Safe:
        effect = dict_JH_Octavia
    elif effect == dict_JH_Fuzz_Tone_Safe:
        effect = dict_JH_Fuzz_Tone
    elif effect == dict_JH_Voodoo_Vibe_Jr_Safe:
        effect = dict_JH_Voodoo_Vibe_Jr
    return effect

def get_js_effect_name(effect):
        # Modify amp IDs to make them JS friendly
        if effect == dict_bias_noisegate:
            effect = dict_bias_noisegate_safe
        elif effect == dict_AC_Boost:
            effect = dict_AC_Boost_safe        
        elif effect == dict_JH_Vox_846:
            effect = dict_JH_Vox_846_Safe
        elif effect == dict_JH_Dual_Showman:
            effect = dict_JH_Dual_Showman_Safe
        elif effect == dict_JH_Sunn_100:
            effect = dict_JH_Sunn_100_Safe
        elif effect == dict_JH_JTM45:
            effect = dict_JH_JTM45_Safe
        elif effect == dict_JH_Bassman_Silver:
            effect = dict_JH_Bassman_Silver_Safe
        elif effect == dict_JH_Super_Lead_100:
            effect = dict_JH_Super_Lead_100_Safe
        elif effect == dict_JH_Sound_City_100:
            effect = dict_JH_Sound_City_100_Safe
        elif effect == dict_JH_Axis_Fuzz:
            effect = dict_JH_Axis_Fuzz_Safe
        elif effect == dict_JH_Supa_Fuzz:
            effect = dict_JH_Supa_Fuzz_Safe
        elif effect == dict_JH_Octavia:
            effect = dict_JH_Octavia_Safe
        elif effect == dict_JH_Fuzz_Tone:
            effect = dict_JH_Fuzz_Tone_Safe
        elif effect == dict_JH_Voodoo_Vibe_Jr:
            effect = dict_JH_Voodoo_Vibe_Jr_Safe
        return effect