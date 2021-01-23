$( document ).ready(function() {
    $('#connect').on('click',function(e){
        e.preventDefault();
        $('#connect').prop( 'disabled', true )
        $('#connection-log').html('');
        $.post('/connect');
    });    

    $('.preset_button').on('click', function(){        
        if ($(this).hasClass('selected')){
            return;
        }

        var preset = $(this).val();

        $('.preset_button').removeClass('selected');                
        $('#preset_' + preset).addClass('selected');

        var data = {'preset': preset};
        
        $.post('/changepreset', data);

        $('.loading').show();
    })

    $(document).on('click', '.onoff_button', function(){
        
        if ($(this).hasClass('selected')){
            return;
        }

        var id = $(this).data('id');
        var state = $(this).val();
        var data = {'id': id, 'state': state};

        $.post('/turneffectonoff', data);
        
        if (state === 'Off'){
            $('#' + id + '_off').addClass('selected');
            $('#' + id + '_on').removeClass('selected');            
        } else{
            $('#' + id + '_on').addClass('selected');
            $('#' + id + '_off').removeClass('selected');            
        }        
    });

    $(document).on('change','[type=range]', function(){
        var id = $(this).data('id');
        var param = $(this).data('parameter');
        var value = $(this).val();

        var data = {'id': id, 'parameter': param, 'value': value };

        $.post('/changeeffectparameter', data);
      });

    $(document).on('change', '[type=checkbox]', function(){
        var id = $(this).data('id');
        var param = $(this).data('parameter');
        var value = 0.0000

        if ($(this).is(":checked")){
            value = 1.0000
        }

        var data = {'id': id, 'parameter': param, 'value': value };

        $.post('/changeeffectparameter', data);
    });

    $(document).on('change', '.effect-selector', function(){
        var effecttype = $(this).data('type');
        var oldeffect = $(this).data('selected');
        var neweffect = $(this).val()

        var data = {'oldeffect': oldeffect, 'neweffect': neweffect, 'effecttype': effecttype, 'logchangeonly': false};        

        $('#' + effecttype + '_container').load('/changeeffect', data);        
    });

    $('#eject').on('click', function(){
        var data = {'eject': true}
        $.post('/eject', data);        
    })
  });
