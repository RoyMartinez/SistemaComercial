$(document).ready(function(){
    var ShowForm= function(){
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type : 'get',
            dataType:'json',
            beforeSend: function(){
                $('#modal-Pantalla').modal('show');
            },
            success: function(data){
                $('#modal-Pantalla .modal-content').html(data.html_form);
            }
        });
    };

    var SaveForm = function(){
        var form = $(this);
        $.ajax({
            url: form.attr('data-url'),
            data: form.serialize(),
            type: form.attr('method'),
            dataType : 'json',
            success: function(data){
                if(data.form_is_valid){
                    $('#Pantalla-table tbody').html(data.Pantalla_List);
                    $('#modal-Pantalla').modal('hide');
                } else{
                    $('#modal-Pantalla .modal-content').html(data.html_form);
                }
            }
        });
        return false;
    };
    // create
    $(".show-form").click(ShowForm);
    $(".show-form-update").click(ShowForm);
    $("#modal-Pantalla").on("submit",".create-form",SaveForm);
    //update
    $("#Pantalla-table").on("click",".show-form-update",ShowForm);
    $("#modal-Pantalla").on("submit",".update-form",SaveForm);
    //delete
    $("#Pantalla-table").on("click",".show-form-delete",ShowForm);
    $("#modal-Pantalla").on("submit",".delete-form",SaveForm);
    
    // Control para bloquear 
    $('input[type=number]').prop('min','0');
    // $('input[type=number]').on('keypress',function(){
    //     return event.charCode <= 57 && event.charCode >= 48;
    // });
    $('input[type=number]').on('keypress',function(){
        console.log(e.keyCode);
        if (e.keyCode == 101 || e.keyCode == 46 /*|| e.keyCode == 45*/ || e.keyCode == 43 || e.keyCode == 44 || e.keyCode == 47) {
            return false;
        }
        soloNumeros(e.keyCode);
    });
    
    function soloNumeros(e) {
        var key = window.Event ? e.which : e.keyCode
            return (key >= 48 && key <= 57)
    }
});