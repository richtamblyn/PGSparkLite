var socket = io();

// Update On/Off UI elements
function changeOnOffState(state, effect, type) {
  amp_preset_modified();
  if (state === "Off") {
    $("#" + effect + "_off").addClass("selected");
    $("#" + effect + "_on").removeClass("selected");
    $("#" + type + "_container").addClass("grayscale");
  } else {
    $("#" + effect + "_on").addClass("selected");
    $("#" + effect + "_off").removeClass("selected");
    $("#" + type + "_container").removeClass("grayscale");
  }
}

// Global toasts function
function notify_user(message) {
  alerty.toasts(
    message,
    {
      bgColor: "green",
      fontColor: "white",
    },
    function () {
      $(".loading").hide();
    }
  );
}

// If preset is modified, notify user by flashing the preset button
function amp_preset_modified(){
  $(".preset_button.selected").addClass("flash");
}

function amp_preset_stored(data){
  $(".preset_button.selected").removeClass("flash");
  notify_user(data.message)
}

function showHideContent(effect_type, effect, visible) {
  var chevron = $("#" + effect_type + "_showhidecontent");
  var content = $("#" + effect + "_content");
  if (visible) {
    content.slideDown("slow");
    chevron.removeClass("collapse_closed");
    chevron.addClass("collapse_open");
  } else {
    content.slideUp("slow");
    chevron.removeClass("collapse_open");
    chevron.addClass("collapse_closed");
    visible = false;
  }
}

// Knob changes have to be caught by this handler explicitly stated in HTML instead of JQuery element event.
function knobChangeEventHandler(knob) {
  amp_preset_modified();
  var effect = knob.dataset["id"];
  var param = knob.dataset["parameter"];
  var value = knob.value;
  var data = { effect: effect, parameter: param, value: value };
  socket.emit("change_effect_parameter", data);
}

function updateChainPreset(preset_id, name) {
  $(".loading").show();

  var data = {
    name: name,
    preset_id: preset_id,
  };

  $.post("/chainpreset/update", data, function (result) {
    $("#chain_preset_container").html(result);
    notify_user("The chain preset was saved successfully.");
  });
}

function updatePedalPreset(effecttype, preset_id, name) {
  $(".loading").show();

  var data = {
    effect_type: effecttype,
    name: name,
    preset_id: preset_id,
  };

  $.post("/pedalpreset/update", data, function (result) {
    $("#" + effecttype + "_footer").html(result);
    notify_user("The pedal preset was saved successfully.");
  });
}