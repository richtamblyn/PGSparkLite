var socket = io();

function changeOnOffState(state, effect, type){
    if (state === 'Off') {
        $('#' + effect + '_off').addClass('selected');
        $('#' + effect + '_on').removeClass('selected');
        $('#' + type + '_container').addClass('grayscale');
    } else {
        $('#' + effect + '_on').addClass('selected');
        $('#' + effect + '_off').removeClass('selected');
        $('#' + type + '_container').removeClass('grayscale');
    }
}

function knobChangeEventHandler(knob) {
    var effect = knob.dataset['id'];
    var param = knob.dataset['parameter'];
    var value = knob.value;
    var data = { 'effect': effect, 'parameter': param, 'value': value };
    socket.emit('change_effect_parameter', data)
};

function updateChainPreset(preset_id, namerequired){
    if(namerequired){
        var name = prompt('Please enter a name for new preset');
        if (name == null) {                    
            return;
        }
    }

    var data = {
        'name': name,
        'preset_id':preset_id
    };

    $.post('/updatechainpreset', data, function (result){
        $('#chain_preset_container').html(result);
        alert('The preset was saved successfully.');
    })
}

function updatePedalPreset(effecttype, preset_id, namerequired){
    if(namerequired){
        var name = prompt('Please enter a name for new preset');
        if (name == null) {                    
            return;
        }
    }
        
    var data = {        
        'effect_type': effecttype,
        'name': name,        
        'preset_id': preset_id        
    };

    $.post('/updatepedalpreset', data, function (result) {
        $('#' + effecttype + '_footer').html(result);
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

        window.changeOnOffState(state, effect, type);
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

        var data = { 'old_effect': oldeffect, 'new_effect': neweffect, 'effect_type': effecttype, 'log_change_only': false };

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
        var effecttype = $(this).data('type');        
        var visible = true;

        if ($(this).hasClass('collapse_open')) {
            $('#' + effect + '_content').slideUp('slow');
            $(this).removeClass('collapse_open');
            $(this).addClass('collapse_closed');            
            visible = false;
        } else
        {
            $('#' + effect + '_content').slideDown('slow');
            $(this).removeClass('collapse_closed');
            $(this).addClass('collapse_open');
        }

        var data = {'effect_type':effecttype, 'visible':visible}
        socket.emit('show_hide_pedal', data);
    });

    // Chain Presets
    $(document).on('click','#new_chain_preset', function(){
        updateChainPreset(0, true);
    });

    $(document).on('click','#save_chain_preset', function(){
        var preset_id = $('#chain_preset_selector').val()
        var name_required = false;
        if(preset_id == 0){
            name_required = true;
        }
        updateChainPreset(preset_id, name_required);
    });

    $(document).on('change', '#chain_preset_selector', function () {
        var preset_id = $(this).val();
        if(preset_id == 0){
            return;
        }
        
        socket.emit('change_chain_preset', {'preset_id':preset_id})
    });

    // Pedal Presets

    $(document).on('click', '.new_pedal_preset', function () {                
        updatePedalPreset($(this).data('type'), 0, true);
    });

    $(document).on('click', '.save_pedal_preset', function () {        
        var effecttype = $(this).data('type');
        var preset_id = $('#' + effecttype + '_pedal_preset_selector').val();
        var name_required = false;
        if(preset_id == 0){
            name_required = true;
        } 
        updatePedalPreset(effecttype, preset_id, name_required);
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
