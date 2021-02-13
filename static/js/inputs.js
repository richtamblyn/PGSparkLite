var socket = io();

function knobChangeEventHandler(knob) {
    var effect = knob.dataset['id'];
    var param = knob.dataset['parameter'];
    var value = knob.value;
    var data = { 'effect': effect, 'parameter': param, 'value': value };
    socket.emit('change_effect_parameter', data)
};

function getParametersByEffectName(effect) {
    var numOfParameters = $('#' + effect + '_parameters').data('num');
    var parameters = [];

    for (var p = 0; p != numOfParameters; p++) {
        parameters.push($('#' + effect + '_' + p).val());
    }

    return JSON.stringify(parameters);
}

function getOnOffStateByEffectName(effect) {
    if ($('#' + effect + '_on').hasClass('selected')) {
        return 'On'
    } else {
        return 'Off'
    }
}

function updatePedalPreset(effect, effecttype, preset_id, namerequired){
    if(namerequired){
        var name = prompt('Please enter a name for new preset');
        if (name == null) {        
            alert('You must enter a name for the preset.');
            return;
        }
    }
        
    var data = {
        'effect': effect,
        'effect_type': effecttype,
        'name': name,
        'parameters': getParametersByEffectName(effect),
        'preset_id': preset_id,
        'onoff': getOnOffStateByEffectName(effect)
    };

    $.post('/updatepedalpreset', data, function (result) {
        $('#' + effecttype + '_footer').html(result)
        alert('The preset was saved successfully.');
    });
}

$(document).ready(function () {    
    $('#connect').on('click', function (e) {
        e.preventDefault();
        $('#connect').prop('disabled', true)
        $('#connection-log').html('');
        $.post('/connect');
    });

    $('.preset_button').on('click', function () {
        if ($(this).hasClass('selected')) {
            return;
        }

        var preset = $(this).val();

        $('.preset_button').removeClass('selected');
        $('#preset_' + preset).addClass('selected');

        var data = { 'preset': preset };

        socket.emit('change_preset', data);

        $('.loading').show();
    });

    $(document).on('click', '.onoff_button', function () {
        if ($(this).hasClass('selected')) {
            return;
        }

        var effect = $(this).data('id');
        var state = $(this).val();
        var type = $(this).data('type');
        var data = { 'effect': effect, 'state': state };

        if (state === 'Off') {
            $('#' + effect + '_off').addClass('selected');
            $('#' + effect + '_on').removeClass('selected');
            $('#' + type + '_container').addClass('grayscale');
        } else {
            $('#' + effect + '_on').addClass('selected');
            $('#' + effect + '_off').removeClass('selected');
            $('#' + type + '_container').removeClass('grayscale');
        }

        socket.emit('turn_effect_onoff', data);
    });

    $(document).on('change', '[type=checkbox]', function () {
        var effect = $(this).data('id');
        var param = $(this).data('parameter');
        var value = 0.0000

        if ($(this).is(":checked")) {
            value = 1.0000
        }

        $(this).val(value);

        var data = { 'effect': effect, 'parameter': param, 'value': value };

        socket.emit('change_effect_parameter', data);
    });

    $(document).on('change', '.effect_selector', function () {
        var effecttype = $(this).data('type');
        var oldeffect = $(this).data('selected');
        var neweffect = $(this).val()

        var data = { 'oldeffect': oldeffect, 'neweffect': neweffect, 'effecttype': effecttype, 'logchangeonly': false };

        $('#' + effecttype + '_container').load('/changeeffect', data);
    });

    $('#eject').on('click', function () {
        socket.emit('eject')
    });

    $('#reset-config').on('click', function () {
        socket.emit('reset_config');
    });

    $(document).on('click', '.showhidecontent', function () {
        var effect = $(this).data('id');        
        if ($(this).hasClass('collapse_open')) {
            $('#' + effect + '_content').slideUp('slow');
            $(this).removeClass('collapse_open');
            $(this).addClass('collapse_closed');
        } else
        {
            $('#' + effect + '_content').slideDown('slow');
            $(this).removeClass('collapse_closed');
            $(this).addClass('collapse_open');
        }
    })

    // Pedal Presets

    $(document).on('click', '.new_pedal_preset', function () {
        var effect = $(this).data('id');
        var effecttype = $(this).data('type');        
        updatePedalPreset(effect, effecttype, 0, true);
    });

    $(document).on('click', '.save_pedal_preset', function () {
        var effect = $(this).data('id');
        var effecttype = $(this).data('type');
        var preset_id = $('#' + effecttype + '_pedal_preset_selector').val()
        var namerequired = false
        if(preset_id == 0){
            namerequired = true;
        } 
        updatePedalPreset(effect, effecttype, preset_id, namerequired);
    });

    $(document).on('click', '.delete_pedal_preset', function () {
        var effecttype = $(this).data('type');            
        var preset_id = $('#' + effecttype + '_pedal_preset_selector').val();
        if(preset_id == 0){
            return;
        }

        if (confirm("Are you sure you want to delete this preset?")) {            
            var data = {
                'effect_type': effecttype,
                'preset_id': preset_id
            };

            $.post('/deletepedalpreset', data, function (result) {
                $('#' + effecttype + '_footer').html(result)
                alert('The preset was deleted successfully.');
            });
        };
    })

    $(document).on('change', '.pedal_preset_selector', function () {
        var preset_id = $(this).val();
        if(preset_id == 0){
            return;
        }

        var effecttype = $(this).data('type');
        var data = {
            'effect_name': $(this).data('id'),
            'effect_type': effecttype,
            'preset_id': preset_id,
        };

        $.post('/changepedalpreset', data, function (result) {
            $('#' + effecttype + '_container').html(result);            
        });
    })
});
