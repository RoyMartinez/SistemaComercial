$(document).ready(function(){
    
// ************** Modal Cedula **************************
    $('#txtcedula').on('change', obtenerid);
    $('#txtcedula').on('paste',function(e){
        e.preventDefault();
    });
    $('#txtauth').on('paste', function(e){
        e.preventDefault();
    })
    $('#btn_cliente').on('click', tiempo);

    alertacredito();

// ************** Check out for a registered customer and a custom one **************************
    $('#cliente_personalizado').on('change', predeterminar_cliente);

// ************** Prevenir Form Submit al presionar la tecla ENTER **************************
    $('.prevenir').keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == '13'){
            event.preventDefault();
        }
    });
});
// ************** Timer that hides modal after x seconds  **************************
function tiempo(){
    $('#desc').prop('checked',false);
    $('#xtra').css('display','none');
    $('#xinput').val(0);
    $('#txtcedula').val('');
    setTimeout(function(){
        $('#modalcliente').modal('hide');
    },2500);
}
// ************** Mostrar u ocultar el DIV de alerta por suficiencia de credito ****
function alertacredito(){
    if ($('#id_formapago').val()==4){ 
        var disponible = parseFloat($('#txtsaldo').html());
        var total = parseFloat($('#txt_total').val());
        if (disponible < total)  
            $('#insuficiente').css('display','block');
        else
            $('#insuficiente').css('display','none');
    }
}

// ************** Change focus to Cedula text input modal **************************
$('#modalcliente').on('shown.bs.modal', function () {
    $('#txtcedula').val('');
    $('#txtcedula').focus();
});

$('#modalxtradisccount').on('shown.bs.modal', function () {
    $('#txtauth').val('');
    $('#txtauth').focus();
    setTimeout(function(){
        $('#modalxtradisccount').modal('hide');
        if ($('#txtauth').val() == ''){
            $('#xtra').css('display','none');
            $('#desc').prop('checked',false);
        }
    },2500);
});

// ************** Switch CCT **************************
$('#cct').on('change',function(){
    var auxiliar = parseFloat($('#iva_aux').val());
    if($('#cct').prop('checked')){ //Si el interruptor esta en ON
        var iva = parseFloat($('#txt_iva').val());
        if (iva==0){
            alert('No hay nada que exonerar');
            $('#cct').prop('checked',false);
        }else{
            $('#cct_cuadro').css('display','block');
        }
    }else{ 
        var exoneracion = $('#cct_cuadro input');
        exoneracion[0].value = '0';
        exoneracion[1].value = 0;
        $('#txt_iva').val($('#iva_aux').val());
        $('#txt_total').val($('#txt_st').val() - $('#id_descuentotal').val() + auxiliar );
        $('#cct_cuadro').css('display','none'); 
        alertacredito();
    }
});

$('#cct_cuadro input').on('change',function(){
    var auxiliar = parseFloat($('#iva_aux').val());
    var exoneracion = $('#cct_cuadro input');  
    if ((exoneracion[0].value.length >=2)  && (parseFloat(exoneracion[1].value) == auxiliar)){
        $('#txt_iva').val(0);
        $('#txt_total').val($('#txt_st').val() - $('#id_descuentotal').val());
        alertacredito();
    }else{
        $('#txt_iva').val($('#iva_aux').val());
        $('#txt_total').val(($('#txt_st').val() - $('#id_descuentotal').val() + auxiliar).toFixed(2));
        alertacredito();
    }
});

// ************** Switch XtraDescuento **************************
$('#desc').on('change',function(){
    if($('#desc').prop('checked')){ //Si el interruptor esta en ON
        $('#modalxtradisccount').modal('show');
    }else{ 
        $('#desc').prop('checked',false);
        $('#xtra').css('display','none');
        $('#xinput').val(0);
        combos();
    }
});

// ************** Codigo de autorizado **************************
$('#txtauth').on('change', function(){
    var request = $.ajax({
        type:"GET",
        url:"/ventas/ajax/extra/descuento/verificar/acceso/",
        data:{'codigo': this.value,}
    });
    request.done(function(response){
        if (response.acceso){
            $('#xtra').css('display','block');
        } else{
            alert('Acceso no autorizado');
            $('#xtra').css('display','none');
            $('#desc').prop('checked',false);
        }
    });
});
