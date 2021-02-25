var socket = io();

function changeOnOffState(state, effect, type) {
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

function notify_user(message) {
  alerty.toasts(
    message,
    {
      bgColor: 'green',
      fontColor: 'white',
    },
    function () {
      $('.loading').hide();
    }
  );
}

function showHideContent(effect_type, effect, visible) {
  var chevron = $('#' + effect_type + '_showhidecontent');
  var content = $('#' + effect + '_content');
  if (visible) {
    content.slideDown('slow');
    chevron.removeClass('collapse_closed');
    chevron.addClass('collapse_open');
  } else {
    content.slideUp('slow');
    chevron.removeClass('collapse_open');
    chevron.addClass('collapse_closed');
    visible = false;
  }
}

function knobChangeEventHandler(knob) {
  var effect = knob.dataset['id'];
  var param = knob.dataset['parameter'];
  var value = knob.value;
  var data = { effect: effect, parameter: param, value: value };
  socket.emit('change_effect_parameter', data);
}

function updateChainPreset(preset_id, name) {
  $('.loading').show();

  var data = {
    name: name,
    preset_id: preset_id,
  };

  $.post('/chainpreset/update', data, function (result) {
    $('#chain_preset_container').html(result);
    notify_user('The chain preset was saved successfully.');
  });
}

function updatePedalPreset(effecttype, preset_id, name) {
  $('.loading').show();

  var data = {
    effect_type: effecttype,
    name: name,
    preset_id: preset_id,
  };

  $.post('/pedalpreset/update', data, function (result) {
    $('#' + effecttype + '_footer').html(result);
    notify_user('The pedal preset was saved successfully.');
  });
}

$(document).ready(function () {
  $('#connect').on('click', function (e) {
    e.preventDefault();
    $('#connect').prop('disabled', true);
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

    var data = { preset: preset };

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
    var data = { effect_type: type };

    window.changeOnOffState(state, effect, type);
    socket.emit('toggle_effect_onoff', data);
  });

  $(document).on('change', '[type=checkbox]', function () {
    var effect = $(this).data('id');
    var param = $(this).data('parameter');
    var value = 0.0;

    if ($(this).is(':checked')) {
      value = 1.0;
    }

    $(this).val(value);

    var data = { effect: effect, parameter: param, value: value };

    socket.emit('change_effect_parameter', data);
  });

  $(document).on('change', '.effect_selector', function () {
    var effecttype = $(this).data('type');
    var oldeffect = $(this).data('selected');
    var neweffect = $(this).val();

    var data = {
      old_effect: oldeffect,
      new_effect: neweffect,
      effect_type: effecttype,
      log_change_only: false,
    };

    $('#' + effecttype + '_container').load('/effect/change', data);
  });

  $('#eject').on('click', function () {
    socket.emit('eject');
  });

  $('#reset-config').on('click', function () {
    socket.emit('reset_config');
  });

  $(document).on('click', '.showhidecontent', function () {
    var effect = $(this).data('id');
    var effect_type = $(this).data('type');
    var visible = true;

    if ($(this).hasClass('collapse_open')) {
      visible = false;
    }

    showHideContent(effect_type, effect, visible);

    var data = { effect_type: effect_type, visible: visible };
    socket.emit('show_hide_pedal', data);
  });

  // Chain Presets
  $(document).on('click', '#new_chain_preset', function () {
    alerty.prompt(
      'Please enter a name for the chain preset.',
      { inputType: 'text', inputPlaceholder: 'New chain preset name' },
      function (name) {
        if (name == null || name == '') {
          alerty.alert(
            'You must enter a name!',
            {
              title: 'Error',
              time: 3000,
            },
            function () {
              return;
            }
          );
        } else {
          updateChainPreset(0, name);
        }
      }
    );
  });

  $(document).on('click', '#save_chain_preset', function () {
    var preset_id = $('#chain_preset_selector').val();
    if (preset_id == 0) {
      return;
    }
    updateChainPreset(preset_id, null);
  });

  $(document).on('click', '#delete_chain_preset', function () {
    var preset_id = $('#chain_preset_selector').val();
    if (preset_id == 0) {
      return;
    }

    alerty.confirm(
      'Are you sure you want to delete this preset?',
      {
        title: 'Confirm Chain Preset Delete',
        cancelLabel: 'No',
        okLabel: 'Yes',
      },
      function () {
        $('.loading').show();
        var data = {
          preset_id: preset_id,
        };

        $.post('/chainpreset/delete', data, function (result) {
          $('#chain_preset_container').html(result);
          notify_user('The chain preset was deleted successfully.');
        });
      }
    );
  });

  $(document).on('change', '#chain_preset_selector', function () {
    var preset_id = $(this).val();
    if (preset_id == 0) {
      return;
    }

    $('#loading').show();
    $('#chain_preset_form').submit();
  });

  // Pedal Presets

  $(document).on('click', '.new_pedal_preset', function () {
    var effect_type = $(this).data('type');
    alerty.prompt(
      'Please enter a name for the pedal preset.',
      { inputType: 'text', inputPlaceholder: 'New pedal preset name' },
      function (name) {
        if (name == null || name == '') {
          alerty.alert(
            'You must enter a name!',
            {
              title: 'Error',
              time: 3000,
            },
            function () {
              return;
            }
          );
        } else {
          updatePedalPreset(effect_type, 0, name);
        }
      }
    );
  });

  $(document).on('click', '.save_pedal_preset', function () {
    var effecttype = $(this).data('type');
    var preset_id = $('#' + effecttype + '_pedal_preset_selector').val();
    if (preset_id == 0) {
      return;
    }
    updatePedalPreset(effecttype, preset_id, null);
  });

  $(document).on('click', '.delete_pedal_preset', function () {
    var effecttype = $(this).data('type');
    var preset_id = $('#' + effecttype + '_pedal_preset_selector').val();
    if (preset_id == 0) {
      return;
    }

    alerty.confirm(
      'Are you sure you want to delete this preset?',
      {
        title: 'Confirm Pedal Preset Delete',
        cancelLabel: 'No',
        okLabel: 'Yes',
      },
      function () {
        $('.loading').show();
        var data = {
          effect_type: effecttype,
          preset_id: preset_id,
        };

        $.post('/pedalpreset/delete', data, function (result) {
          $('#' + effecttype + '_footer').html(result);
          notify_user('The pedal preset was deleted successfully.');
        });
      }
    );
  });

  $(document).on('change', '.pedal_preset_selector', function () {
    var preset_id = $(this).val();
    if (preset_id == 0) {
      return;
    }

    var effect_type = $(this).data('type');
    var effect_name = $(this).data('id');
    var data = {
      effect_name: effect_name,
      effect_type: effect_type,
      preset_id: preset_id,
    };

    $.post('/pedalpreset/change', data, function (result) {
      $('#' + effect_type + '_container').html(result.html);
      window.changeOnOffState(result.on_off, effect_name, effect_type);
    });
  });
});
