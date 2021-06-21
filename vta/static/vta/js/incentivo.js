$("#id_cliente").selectpicker();
$('#txt_producto').selectpicker();

var invalido = ["e"]
$('#txt_dinero').on('input', function(evt){
    $('#txt_total').val(this.value);

    /*var nonNumReg = /[^0-9]/g
    $(this).val($(this).val().replace(nonNumReg, ''));
    if (event.which != 8 && event.which != 0 && (event.which < 48 || event.which > 57)) {
        //$(".alert").html("Enter only digits!").show().fadeOut(2000);
        console.log('gfgfdgfdgfd');
        //return false;
    }else*/
    
});