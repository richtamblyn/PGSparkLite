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

    for (var p = 0; p < numOfParameters; p++) {
        parameters.push($('#' + effect + '_' + p).val());
    }

    return parameters;
}

function getOnOffStateByEffectName(effect) {
    if ($('#' + effect + '_on').hasClass('selected')) {
        return 'On'
    } else {
        return 'Off'
    }
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
    })

    $(document).on('click', '.onoff_button', function () {
        if ($(this).hasClass('selected')) {
            return;
        }

        var effect = $(this).data('id');
        var state = $(this).val();

        var data = { 'effect': effect, 'state': state };

        if (state === 'Off') {
            $('#' + effect + '_off').addClass('selected');
            $('#' + effect + '_on').removeClass('selected');
        } else {
            $('#' + effect + '_on').addClass('selected');
            $('#' + effect + '_off').removeClass('selected');
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
    })

    $('#reset-config').on('click', function () {
        socket.emit('reset_config');
    })

    // Pedal Presets

    $(document).on('click', '.new_pedal_preset', function () {
        var name = prompt('Please enter a name for new preset');
        if (name != null) {
            var effect = $(this).data('id');
            var data = { 'effect': effect, 
                        'name': name, 
                        'parameters': getParametersByEffectName(effect), 
                        'preset_id': 0, 
                        'onoff': getOnOffStateByEffectName(effect) };

            socket.emit('new_pedal_preset', data);
        }
    });

    $(document).on('click', '.save_pedal_preset', function () {
        // Placeholder
    });

    $(document).on('click', '.delete_pedal_preset', function () {
        if (confirm("Are you sure you want to delete this preset?")) {
            // They say yes
        };
    })
});
