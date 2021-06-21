// El titulo de la Factura cambia de Credito o Contado en dependencia de la forma de pago
function cambiarcabecera(){
    var tipo = $('#id_formapago').val();
    if (tipo == 4){
        document.getElementById('encabezado').innerHTML = 'FACTURA DE CREDITO';
    }
    else{
        document.getElementById('encabezado').innerHTML = 'FACTURA DE CONTADO';
    }
    $('#sw-descuento').prop('checked',false);
    document.querySelector('#id_descuentotal').value = 0.00;
    document.querySelector('#txtIVA').innerHTML = (document.querySelector('#txtSubTotal').innerHTML *0.15).toFixed(2);
    document.querySelector('#txtTotal').innerHTML = (document.querySelector('#txtSubTotal').innerHTML * 1.15).toFixed(2);
}

// Captura el numero de cedula del modal de seleccion de clientes
function obtenerid(){
    var cedula = document.querySelector('#txtcedula').value;
    var request = $.ajax({
        type:"GET",
        //url: "{% url 'url_ajax_cliente' %}",
        url: 'http://localhost:8000/ventas/ajax/cliente/',
        data: {"cedula":cedula,},
    });
    request.done(function(response){
        document.getElementById('pcliente').innerHTML = response.datos;
        document.getElementById('cliente_personalizado').value = cedula;
        document.getElementById('cliente_oculto').value = cedula;
        $('#sw-descuento').prop('checked',false);
        document.querySelector('#id_descuentotal').value = 0.00;
        document.querySelector('#txtIVA').innerHTML = (document.querySelector('#txtSubTotal').innerHTML *0.15).toFixed(2);
        document.querySelector('#txtTotal').innerHTML = (document.querySelector('#txtSubTotal').innerHTML * 1.15).toFixed(2);
    });
}


// Calcula precio, subtotal e iva
function multiplicar(valor){
    if (valor.value <= 0){
        alert('No se admiten números negativos ni valores en cero');
        valor.value=1;
    }
    else{
        var numero = valor.id;
        var indice = numero[numero.length-1];
        var precio = document.getElementById('pu-'+indice).innerHTML;
        var cantidad =valor.value;
        document.getElementById('total-'+indice).innerHTML = (cantidad * precio).toFixed(2);
        var tabla = (document.querySelector('.inventory').rows.length)-1;
        var total=0;
        var cant_items = [];
        for(var i=1;i <= tabla;i++){
            y = parseFloat(document.getElementById('total-'.concat(i)).innerHTML);
            total += y;
            cant_items.push(document.getElementById('codigo-'.concat(i)).innerHTML);
            cant_items.push(document.getElementById('cant-'.concat(i)).value);
        }
        $('#sw-descuento').prop('checked',false);
        document.querySelector('#id_descuentotal').value = 0.00;
        document.getElementById('txtSubTotal').innerHTML = total.toFixed(2);
        document.getElementById('txtIVA').innerHTML = (total * 0.15).toFixed(2);
        document.getElementById('txtTotal').innerHTML = (total *1.15).toFixed(2);
        document.getElementById('txtMaestro').innerHTML = (total *1.15).toFixed(2);
        console.log(cant_items);
        var request =$.ajax({type:"GET", 
                                url: 'http://localhost:8000/ventas/ajax/item/actualizar/', 
                                data: {"cantidad":cant_items.toString()}
                                });  
    }
}

// Establece un temporizador de 2500 ms para abrir el modal de entrada de clientes por carnet
function recargar(){
    setTimeout(function(){
        location.reload(true);
        },2500
    );
}