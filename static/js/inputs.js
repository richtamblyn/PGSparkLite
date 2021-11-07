$(document).ready(function () {
  var start, end, diff;
  var clickTime = 500;

  $("#connect").on("click", function (e) {
    e.preventDefault();
    $("#connect").prop("disabled", true);
    $("#connection-log").html("");
    $.post("/connect");
  });

  $(".preset_button").on("mousedown", function () {
    start = Date.now();
  });

  $(".preset_button").on("mouseup", function () {
    end = Date.now();
    diff = end - start + 1;
    if (diff > clickTime) {
      $(".loading").show();
      socket.emit("store_amp_preset");
    } else {
      var preset = $(this).val();

      $(".preset_button").removeClass("selected");
      $("#preset_" + preset).addClass("selected");

      var data = { preset: preset };

      socket.emit("change_preset", data);

      $(".loading").show();
    }
  });

  $(document).on("click", ".onoff_button", function () {
    if ($(this).hasClass("selected")) {
      return;
    }

    var effect = $(this).data("id");
    var state = $(this).val();
    var type = $(this).data("type");
    var data = { effect_type: type };

    window.changeOnOffState(state, effect, type);
    socket.emit("toggle_effect_onoff", data);
  });

  $(document).on("dblclick", ".input-knob", function(){
    var effect = $(this).data("id");
    var param = $(this).data("parameter");
    var expression = $(this).data("expression");
    var enabled = true;

    if(expression === undefined || expression === false){
      $(this).data("expression", true);   
      clearExpressionStyles();
      $(this).parent().addClass("expression_param");
    } else {
      $(this).data("expression", false);
      clearExpressionStyles();
      enabled = false;
    }

    var data = { effect: effect, parameter: param, enabled: enabled}
    socket.emit("set_expression_param", data);
  });

  $(document).on("dblclick", ".onoff_button", function(){
    var effect = $(this).data("id");    
    var expression = $(this).data("expression");
    var effect_type = $(this).data("type");
    var enabled = true;

    if(expression === undefined || expression === false){
      $(this).data("expression", true);   
      clearExpressionStyles();
      $(this).parent().addClass("expression_onoff");
    } else {
      $(this).data("expression", false);
      clearExpressionStyles();
      enabled = false;
    }

    var data = { effect: effect, enabled: enabled, effect_type: effect_type }
    socket.emit("set_expression_onoff", data);
  });

  $(document).on("change", "[type=checkbox]", function () {
    window.amp_preset_modified();
    var effect = $(this).data("id");
    var param = $(this).data("parameter");
    var value = 0.0;

    if ($(this).is(":checked")) {
      value = 1.0;
    }

    $(this).val(value);

    var data = { effect: effect, parameter: param, value: value };

    socket.emit("change_effect_parameter", data);
  });

  $(document).on("change", ".effect_selector", function () {
    window.amp_preset_modified();

    var effecttype = $(this).data("type");
    var oldeffect = $(this).data("selected");
    var neweffect = $(this).val();

    var data = {
      old_effect: oldeffect,
      new_effect: neweffect,
      effect_type: effecttype,
      log_change_only: false,
    };

    $("#" + effecttype + "_container").load("/effect/change", data);
  });

  $("#eject").on("click", function () {
    socket.emit("eject");
  });

  $("#reset-config").on("click", function () {
    socket.emit("reset_config");
  });

  $(document).on("click", ".showhidecontent", function () {
    var effect = $(this).data("id");
    var effect_type = $(this).data("type");
    var visible = true;

    if ($(this).hasClass("collapse_open")) {
      visible = false;
    }

    window.showHideContent(effect_type, effect, visible);

    var data = { effect_type: effect_type, visible: visible };
    socket.emit("show_hide_pedal", data);
  });

  // Chain Presets
  $(document).on("click", "#new_chain_preset", function () {
    alerty.prompt(
      "Please enter a name for the chain preset.",
      { inputType: "text", inputPlaceholder: "New chain preset name" },
      function (name) {
        if (name == null || name == "") {
          alerty.alert(
            "You must enter a name!",
            {
              title: "Error",
              time: 3000,
            },
            function () {
              return;
            }
          );
        } else {
          window.updateChainPreset(0, name);
        }
      }
    );
  });

  $(document).on("click", "#save_chain_preset", function () {
    var preset_id = $("#chain_preset_selector").val();
    if (preset_id == 0) {
      return;
    }
    window.updateChainPreset(preset_id, null);
  });

  $(document).on("click", "#delete_chain_preset", function () {
    var preset_id = $("#chain_preset_selector").val();
    if (preset_id == 0) {
      return;
    }

    alerty.confirm(
      "Are you sure you want to delete this preset?",
      {
        title: "Confirm Chain Preset Delete",
        cancelLabel: "No",
        okLabel: "Yes",
      },
      function () {
        $(".loading").show();
        var data = {
          preset_id: preset_id,
        };

        $.post("/chainpreset/delete", data, function (result) {
          $("#chain_preset_container").html(result);
          window.notify_user("The chain preset was deleted successfully.");
        });
      }
    );
  });

  $(document).on("change", "#chain_preset_selector", function () {
    var preset_id = $(this).val();
    if (preset_id == 0) {
      return;
    }

    $("#loading").show();
    $("#chain_preset_form").submit();
  });

  // Pedal Presets

  $(document).on("click", ".new_pedal_preset", function () {
    var effect_type = $(this).data("type");
    alerty.prompt(
      "Please enter a name for the pedal preset.",
      { inputType: "text", inputPlaceholder: "New pedal preset name" },
      function (name) {
        if (name == null || name == "") {
          alerty.alert(
            "You must enter a name!",
            {
              title: "Error",
              time: 3000,
            },
            function () {
              return;
            }
          );
        } else {
          window.updatePedalPreset(effect_type, 0, name);
        }
      }
    );
  });

  $(document).on("click", ".save_pedal_preset", function () {
    var effecttype = $(this).data("type");
    var preset_id = $("#" + effecttype + "_pedal_preset_selector").val();
    if (preset_id == 0) {
      return;
    }
    window.updatePedalPreset(effecttype, preset_id, null);
  });

  $(document).on("click", ".delete_pedal_preset", function () {
    var effecttype = $(this).data("type");
    var preset_id = $("#" + effecttype + "_pedal_preset_selector").val();
    if (preset_id == 0) {
      return;
    }

    alerty.confirm(
      "Are you sure you want to delete this preset?",
      {
        title: "Confirm Pedal Preset Delete",
        cancelLabel: "No",
        okLabel: "Yes",
      },
      function () {
        $(".loading").show();
        var data = {
          effect_type: effecttype,
          preset_id: preset_id,
        };

        $.post("/pedalpreset/delete", data, function (result) {
          $("#" + effecttype + "_footer").html(result);
          window.notify_user("The pedal preset was deleted successfully.");
        });
      }
    );
  });

  $(document).on("change", ".pedal_preset_selector", function () {
    var preset_id = $(this).val();
    if (preset_id == 0) {
      return;
    }

    var effect_type = $(this).data("type");
    var effect_name = $(this).data("id");
    var data = {
      effect_name: effect_name,
      effect_type: effect_type,
      preset_id: preset_id,
    };

    $.post("/pedalpreset/change", data, function (result) {
      $("#" + effect_type + "_container").html(result.html);
      window.changeOnOffState(result.on_off, effect_name, effect_type);
    });
  });

  $("#set-bpm").on("click", function () {    
    $.get("/bpm", function(data){      
      alerty.prompt(
        "Set the BPM.",
        { inputType: "number", inputValue: data.bpm },
        function (new_bpm) {
          if (new_bpm == null || new_bpm == 0) {
            alerty.alert(
              "You must enter a BPM.",
              {
                title: "Error",
                time: 3000,
              },
              function () {
                return;
              }
            );
          } else {
            var payload = {
              bpm: new_bpm
            };

            $.post("/bpm", payload);
          }
        }
      );
    });    
  });
});
