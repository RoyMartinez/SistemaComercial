// Usa DataTable en las tablas
$(document).ready(function() {
    $('#dataTable').DataTable({
        "lengthMenu": [[-1,1,15,25,50,100], ["Todos",1,15,25,50,100]],
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
