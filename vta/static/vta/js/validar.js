//Cambia a MAYUSCULA el texto ingresado
function mayuscula(elemento){
    elemento.value = elemento.value.toUpperCase();
}

//Construye la llave combinada para la tabla FAMILIA (Nivel 2)
function cambiar(){
    var rubro= document.getElementById("id_rubro").value;
    var sigla =document.getElementById("id_siglas");
    document.getElementById('id_siglas').value = sigla.value.toUpperCase();
    document.getElementById("id_id_n2").value = rubro + '.' + sigla.value.toUpperCase();
}

//Construye la llave combinada para la tabla PARTE (Nivel 3)
function parte(){
    var consecutivo = document.getElementById('id_consecutivo').value;
    switch(consecutivo.length){
      case 1:
        consecutivo = '00' + consecutivo;
      break;
      case 2:
        consecutivo = '0' + consecutivo;
      break;
    }
    document.getElementById('id_id_n3').value = document.getElementById('id_familia').value + '.' + consecutivo;
}

// Construye la llave combinada para la tabla ITEM (Nivel 4)
function id_item(){
    var parte = document.getElementById('id_parte').value;
    var marca = document.getElementById('id_marca').value;
    var um = document.getElementById('id_medida').value;
    document.getElementById('id_id_n4').value = parte + '.' + marca + '.' + um;
}