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

// ************** Prevent Submit **************************
    /*$(window).keydown(function(event){
        if (event.keyCode == 13){
            event.preventDefault();
            return false;
        }
    });*/

// ************** Modal Producto **************************
    /*$('#tabla-item').DataTable({
        "language":{
            "lengthMenu":"Mostrar  _MENU_  registros por página",
            "zeroRecords":"No se encontraron coincidencias",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty":"No hay registros",
            "infoFiltered":"(filtrado de un total de _MAX_ registros)",
            "search":"Búsqueda:",
            "paginate":{
                "first":"Primero",
                "last":"Último",
                "next":"Siguiente",
                "previous":"Anterior",
            }
        },
        "ordering": false
    });*/


// ************** Check out for a registered customer and a custom one **************************
    $('#cliente_personalizado').on('change', predeterminar_cliente);
    $('#cliente_personalizado').keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == '13'){
            event.preventDefault();
        }
    });
    $('#xinput').keypress(function(event){
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

// ************** Refresh the window after billing **************************
/*$('#btn_facturar').on("click", function(){
    setTimeout(function(){
        location.reload(true);
    },2500);
});*/

// Changing Subtotal, IVA & Total
