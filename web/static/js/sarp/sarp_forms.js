document.getElementById("id_observador_externo").disabled = true

document.getElementById("id_id_observador").addEventListener("change", function() { 
    if (this.value == 0) {
        // document.getElementById("id_id_observador").disabled = true;
        document.getElementById("id_observador_externo").removeAttribute("disabled");
    } else {
        // document.getElementById("id_id_observador").removeAttribute("disabled");
        document.getElementById("id_observador_externo").disabled = true;
    }
});