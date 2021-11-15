$(document).ready(function () {
    
    $(".debug_logging").on("click", function(){
        var state = $(this).val();
        var data = { state: state };
        socket.emit("toggle_debug_logging", data);                
    })
});