// Usa DataTable en las tablas
$(document).ready(function() {
    $('#dataTable').DataTable({
        "language":{
            "lengthMenu":"Mostrar  _MENU_  filas",
            "zeroRecords":"No se encontraron coincidencias",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty":"No hay registros",
            "infoFiltered":"(filtrado de un total de _MAX_ registros)",
            "search":"Buscar:",
            "paginate":{
                "first":"Primero",
                "last":"Último",
                "next":"Siguiente",
                "previous":"Anterior",
            }
        },
        "ordering": false
    });
	$('#Pantalla-table').DataTable({
        "language":{
            "lengthMenu":"Mostrar  _MENU_  filas",
            "zeroRecords":"No se encontraron coincidencias",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty":"No hay registros",
            "infoFiltered":"(filtrado de un total de _MAX_ registros)",
            "search":"Buscar:",
            "paginate":{
                "first":"Primero",
                "last":"Último",
                "next":"Siguiente",
                "previous":"Anterior",
            }
        },
        "ordering": false
    });
});

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})
