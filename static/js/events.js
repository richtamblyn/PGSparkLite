// Process events from Spark Amp control changes
$(document).ready(function () {
  var socket = io();

  // Connection state
  socket.on("connection-message", function (data) {
    $("#connection-log").html("<p>" + data.message + "</p>");
  });

  socket.on("connection-success", function (data) {
    $("#connection-log").html("<p>All done. Loading controls...</p>");
    window.location.href = data.url;
  });

  socket.on("connection-lost", function (data) {
    window.location.href = data.url;
  });

  // Preset button change
  socket.on("update-preset", function (data) {
    $(".preset_button").removeClass("selected");
    $("#preset_" + data.value).addClass("selected");
    $("#loading").show();
  });

  // Change of effect
  socket.on("update-effect", function (data) {
    window.amp_preset_modified();
    $("#" + data.effect_type + "_selector").val(data.new_effect);
    var update = {
      old_effect: data.old_effect,
      new_effect: data.new_effect,
      effect_type: data.effect_type,
      log_change_only: data.log_change_only,
    };
    $("#" + data.effect_type + "_container").load("/effect/change", update);
  });

  // Change of parameter
  socket.on("update-parameter", function (data) {
    window.amp_preset_modified();
    $("#" + data.effect + "_" + data.parameter).val(data.value);
  });

  // Change OnOff status
  socket.on("update-onoff", function (data) {
    window.amp_preset_modified();
    window.changeOnOffState(data.state, data.effect, data.effect_type);
    socket.emit("turn_effect_onoff", data);
  });

  // Refresh OnOff status from Pedal change
  socket.on("refresh-onoff", function (data) {
    window.changeOnOffState(data.state, data.effect, data.effect_type);
  })

  socket.on("show-hide-content", function (data) {
    window.showHideContent(data.effect_type, data.effect, data.visible);
  });

  socket.on("preset-changed", function(data){
    window.amp_preset_modified();
  });

  socket.on("preset-stored", function(data){
    window.amp_preset_stored(data);
  });
  
  socket.on("reload-client-interface", function(data){    
      var searchParams = new URLSearchParams(window.location.search);
      searchParams.set("preset_id", data.preset_id);
      window.location.search = searchParams.toString();
      window.location.reload();
  })

});
