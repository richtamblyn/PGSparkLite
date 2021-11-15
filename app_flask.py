from flask import jsonify, redirect, render_template, request, url_for

from app import amp, app, socketio
from app_utilities import (change_effect, config_request, do_connect,
                           render_effect, update_pedal_state)
from database.service import (create_update_chainpreset,
                              create_update_pedalpreset, database,
                              get_chain_preset_by_id, get_chain_presets,
                              get_pedal_preset_by_id, get_pedal_presets,
                              get_pedal_presets_by_effect_name,
                              verify_delete_chain_preset,
                              verify_delete_pedal_preset)
from lib.common import (dict_bias_noisegate_safe, dict_bpm, dict_bpm_change,
                        dict_chain_preset, dict_change_effect,
                        dict_change_pedal_preset, dict_effect,
                        dict_effect_type, dict_error, dict_false, dict_id,
                        dict_log_change_only, dict_name, dict_Name,
                        dict_new_effect, dict_ok, dict_old_effect,
                        dict_pedal_chain_preset, dict_preset_id)

##################
# Flask Routes
##################


@app.before_request
def _db_connect():
    database.connect()


@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()


@app.route('/bpm', methods=['GET', 'POST'])
def bpm():
    if request.method == 'GET':
        return jsonify(bpm=int(amp.config.bpm))
    else:
        bpm = int(request.form[dict_bpm])
        amp.set_bpm(bpm)
        socketio.emit(dict_bpm_change, {dict_bpm: bpm})
        return dict_ok


@app.route('/effect/change', methods=['POST'])
def change_effect_endpoint():
    old_effect = request.form[dict_old_effect]
    new_effect = request.form[dict_new_effect]
    effect_type = request.form[dict_effect_type]
    log_change_only = request.form[dict_log_change_only]

    if log_change_only == dict_false:
        change_effect(old_effect, new_effect)

    amp.config.update_config(old_effect, dict_change_effect, new_effect)

    selector = True
    if new_effect == dict_bias_noisegate_safe:
        selector = False

    return render_effect(effect_type, selector)


@app.route('/pedalpreset/change', methods=['POST'])
def change_pedal_preset():
    preset_id = int(request.form[dict_preset_id])
    effect_type = str(request.form[dict_effect_type])

    preset = get_pedal_preset_by_id(preset_id)

    update_pedal_state(preset.pedal_parameter)
    amp.config.update_config(effect_type, dict_change_pedal_preset,
                             (preset_id, preset.pedal_parameter.id))

    selector = True
    if preset.pedal_parameter.effect_name == dict_bias_noisegate_safe:
        selector = False

    return jsonify(html=render_effect(effect_type, selector, preset_id),
                   on_off=preset.pedal_parameter.on_off)


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'GET':
        return render_template('connect.html')
    else:
        do_connect()
        return dict_ok


@app.route('/chainpreset/delete', methods=['POST'])
def delete_chain_preset():
    preset_id = int(request.form[dict_preset_id])
    if verify_delete_chain_preset(preset_id):
        chain_presets = get_chain_presets()
        return render_template('chain_preset_selector.html',
                               chain_presets=chain_presets,
                               preset_selected=0)

    return dict_error


@app.route('/pedalpreset/delete', methods=['POST'])
def delete_pedal_preset():
    preset_id = int(request.form[dict_preset_id])
    preset = get_pedal_preset_by_id(preset_id)
    effect_name = preset.effect_name
    verify_delete_pedal_preset(preset_id)
    return render_template('effect_footer.html',
                           effect_name=effect_name,
                           effect_type=str(request.form[dict_effect_type]),
                           presets=get_pedal_presets_by_effect_name(
                               effect_name),
                           preset_selected=0)


@app.route('/effect/footer', methods=['POST'])
def effect_footer():
    effect_name = request.form[dict_effect]
    return render_template('effect_footer.html',
                           effect_name=effect_name,
                           effect_type=request.form[dict_effect_type],
                           presets=get_pedal_presets_by_effect_name(
                               effect_name),
                           preset_selected=int(request.form[dict_preset_id]))


@app.route('/chainpreset/getlist', methods=['GET'])
def get_chainpreset_list():
    presets = []
    for preset in get_chain_presets():
        presets.append({dict_id: preset.id, dict_name: preset.name})
    return jsonify(presets)


@app.route('/', methods=['GET', 'POST'])
def index():
    if amp.connected == False:
        return redirect(url_for('connect'))

    if request.method == 'GET':
        preset_query = request.args.get(dict_preset_id)
        if preset_query == None:
            preset_id = 0
        else:
            preset_id = int(preset_query)
            amp.config.last_call = dict_pedal_chain_preset
    else:
        preset_id = int(request.form[dict_preset_id])
        preset = get_chain_preset_by_id(preset_id)
        amp.send_preset(preset)
        amp.config.last_call = dict_chain_preset
        config_request()

    return render_template('main.html',
                           debug_logging=amp.debug_logging,
                           config=amp.config,
                           pedal_presets=get_pedal_presets(amp.config),
                           chain_presets=get_chain_presets(),
                           preset_selected=preset_id)


@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html',
                           debug_logging=amp.debug_logging)


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/chainpreset/update', methods=['POST'])
def update_chain_preset():
    preset_id = int(request.form[dict_preset_id])
    if preset_id == 0:
        amp.config.initialise_chain_preset(str(request.form[dict_name]))

    preset = create_update_chainpreset(amp.config)
    chain_presets = get_chain_presets()

    amp.config.update_chain_preset_database_ids(preset)

    return render_template('chain_preset_selector.html',
                           chain_presets=chain_presets,
                           preset_selected=preset.id)


@app.route('/pedalpreset/update', methods=['POST'])
def update_pedal_preset():
    preset_id = int(request.form[dict_preset_id])
    effect_type = str(request.form[dict_effect_type])
    preset_name = None
    if preset_id == 0:
        preset_name = str(request.form[dict_name])

    effect = amp.config.get_current_effect_by_type(effect_type)

    preset = create_update_pedalpreset(preset_name, preset_id, effect)
    amp.config.update_config(
        effect_type, dict_change_pedal_preset, (preset.id, preset.pedal_parameter.id))

    return render_template('effect_footer.html',
                           effect_name=effect[dict_Name],
                           effect_type=effect_type,
                           presets=get_pedal_presets_by_effect_name(
                               effect[dict_Name]),
                           preset_selected=preset.id)
