import threading
from ast import literal_eval

from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO, emit

from lib.sparkdevices import SparkDevices
from lib.sparkampserver import SparkAmpServer

#####################
# Application Setup
#####################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sparksrock'

config = None

socketio = SocketIO(app)

amp = SparkAmpServer(callback_url = 'http://127.0.0.1:5000/callback')

##################
# Utility Methods
##################
  
def get_amp_effect_name(effect):
    # Special cases to match internal amp ID

    if effect == 'bias_noisegate':
        effect = 'bias.noisegate'
    elif effect.isdigit():
        effect = 'bias.reverb'
    return effect

def get_js_effect_name(effect):
    # Modify amp IDs to make them JS friendly

    global config
    
    if effect == 'AC Boost':
        effect = 'AC_Boost'
    elif effect == 'bias.reverb':
        effect = config.reverb['Name']

    return effect

##################
# Flask Routes
##################

@app.route('/callback',methods=['POST'])
def callback():    

    global config

    data = literal_eval(request.json)
    
    if 'ConnectionLost' in data:
        amp.connected = False
        socketio.emit('connection-lost', {'url': url_for('connect')})
        return 'ok'
    
    if 'Connected' in data:
        if data['Connected']:            
            socketio.emit('connection-message', {'message':'Retrieving Amp configuration...'})
            amp.initialise()
            return 'ok'
        else:
            socketio.emit('connection-message', {'message':'Connection failed.'})
            return 'ok'

    if 'PresetOneCorrupt' in data:
        amp.connected = False
        message = ('Preset one cannot be read correctly. ' 
        'To resolve this, manually change to preset one on the amp, set all dials to zero and store the preset.'
        'Power cycle the amp, restart PGSparkLite server and try again.')
        socketio.emit('connection-message', {'message': message })
        return 'ok'

    # Preset button changed
    if 'NewPreset' in data:    
        preset = data['NewPreset']
        socketio.emit('update-preset', {'value': preset})                
        amp.request_preset(preset)
        return 'ok'

    # Parse inbound preset changes
    if 'PresetNumber' in data:                    
        if config is not None:
            if config.preset != data['PresetNumber']:
                # Reload the configuration
                config = SparkDevices(data)
                socketio.emit('connection-success', {'url': url_for('index')})
                return 'ok'
            else:
                # The amp sends the original Preset configuration if no changes other than on/off, ignore this
                return 'ok'
        else:
            # Load the preset configuration into memory and reload the UI
            config = SparkDevices(data)
            socketio.emit('connection-success', {'url': url_for('index')})
            return 'ok'
    
    # Change of amp
    if 'OldEffect' in data:  
        if config.last_call == 'change_effect':            
            config.last_call = ''
            return 'ok'

        old_effect = get_js_effect_name(data['OldEffect'])
        new_effect = get_js_effect_name(data['NewEffect'])

        socketio.emit('update-effect',{'old_effect': old_effect, 'effect_type': 'AMP', 'new_effect': new_effect})    
        config.update_config(old_effect, 'change_effect', new_effect)  
        return 'ok'  

    # Effect / Amp changes
    if 'Effect' in data:        

        # Ignore call back after effect is turned off        
        if config.last_call == 'turn_on_off':
            config.last_call = ''
            return 'ok'

        effect = get_js_effect_name(data['Effect'])
        parameter = data['Parameter']
        value = data['Value']               

        config.update_config(effect,'change_parameter', value, parameter)
        socketio.emit('update-parameter',{'effect': effect, 'parameter': parameter, 'value': value})

        # Check if physical knob turn has activated/deactivated this effect                
        state = config.switch_onoff_parameter(effect, parameter, value)

        if state == None:
            return 'ok'
        
        socketio.emit('update-onoff', {'effect': effect, 'state':state})
        config.update_config(effect, 'turn_on_off', state)    

    return 'ok'

@app.route('/changeeffect', methods=['POST'])
def change_effect():

    global config

    old_effect = request.form['oldeffect']
    new_effect = request.form['neweffect'] 
    effect_type = request.form['effecttype']   
    log_change_only = request.form['logchangeonly']

    if log_change_only == 'false':
        if old_effect.isdigit():
            # Changing Reverb just requires change of value on parameter 6        
            amp.change_effect_parameter('bias.reverb', 6, float('0.' + new_effect))
        else:
            amp.change_effect(get_amp_effect_name(old_effect), get_amp_effect_name(new_effect))

        # Prevent loop when changing amp remotely and receiving update from amp
        config.last_call = 'change_effect'

    config.update_config(old_effect, 'change_effect', new_effect)
    
    current_effect = None
    effect_list = None    
    
    if effect_type == 'COMP':
        current_effect = config.comp
        effect_list = config.comps
    elif effect_type == 'DRIVE':
        current_effect = config.drive
        effect_list = config.drives
    elif effect_type == 'AMP':
        current_effect = config.amp
        effect_list = config.amps        
    elif effect_type == 'MODULATION':
        current_effect = config.modulation
        effect_list = config.modulations
    elif effect_type == 'DELAY':
        current_effect = config.delay
        effect_list = config.delays
    elif effect_type == 'REVERB':
        current_effect = config.reverb
        effect_list = config.reverbs

    if current_effect == None:
        return 'error'

    return render_template('effect.html', 
                            effect_type = effect_type, 
                            effect = current_effect, 
                            effect_list = effect_list,                             
                            selector = True)

@app.route('/changeeffectparameter', methods=['POST'])
def change_effect_parameter():

    effect = request.form['id']
    parameter = int(request.form['parameter'])
    value = float(request.form['value'])

    amp.change_effect_parameter(get_amp_effect_name(effect), parameter, value)

    config.update_config(effect,'change_parameter', value, parameter)

    return 'ok'

@app.route('/changepreset', methods=['POST'])
def change_preset():

    preset = request.form['preset']

    amp.change_to_preset(int(preset))

    return 'ok'

@app.route('/connect', methods=['GET','POST'])
def connect():    
    if request.method == 'GET':
        return render_template('connect.html')
    else:
        # Start a separate thread to connect to the amp, keep user posted via SocketIO
        socketio.emit('connection-message', {'message':'Attempting to connect...'})

        connection = threading.Thread(target=amp.connect, args=(), daemon=True)
        connection.start()        

        return 'ok'

@app.route('/', methods=['GET'])
def index():        
    if amp.connected == False:
        return redirect(url_for('connect'))

    global config

    return render_template('main.html', config = config) 
    
@app.route('/eject', methods=['POST'])
def eject():

    global config

    eject = request.form['eject']
    if eject == 'true':
        config = None
        amp.eject()
        socketio.emit('connection-lost', {'url': url_for('connect')})

    return 'ok'

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

@app.route('/turneffectonoff', methods=['POST'])
def turn_effect_onoff():

    global config

    effect = request.form['id']    
    state = request.form['state']        

    amp.turn_effect_onoff(get_amp_effect_name(effect), state)

    config.update_config(effect, 'turn_on_off', state)    

    config.last_call = 'turn_on_off'

    return 'ok'

if __name__ == '__main__':        
    socketio.run(app)    
