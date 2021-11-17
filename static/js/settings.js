$(document).ready(function () {
    
    $(".debug_logging").on("click", function(){
        $(".debug_logging").prop("checked", false);
        $(this).prop("checked",true);
        var state = $(this).val();
        var data = { state: state };
        socket.emit("toggle_debug_logging", data);
        window.notify_user("Debug Logging setting changed successfully.");
    });

    $(".disable_expression_pedal").on("click", function(){
        $(".disabled_expression_pedal").prop("checked", false);
        $(this).prop("checked",true);
        var state = $(this).val();
        var data = { state: state };
        socket.emit("toggle_expression_pedal", data);
        window.notify_user("Disable Expression Pedal setting changed successfully.");
    });
});