document.getElementById("id_observador_externo").disabled = true;

// ELiminar Opcion "Externo" en Jefe de Comision
function eliminarOpciones(select_id, opc) {
    const select = document.getElementById(`${select_id}`);
    const opcionesAEliminar = [`${opc}`]; // Valores de las opciones a eliminar
  
    for (let i = select.options.length - 1; i >= 0; i--) {
      if (opcionesAEliminar.includes(select.options[i].value)) {
        select.remove(i);
      }
    }
  }
  
  eliminarOpciones("id_id_operador", "0");

document
  .getElementById("id_id_observador")
  .addEventListener("change", function () {
    if (this.value == 0) {
      // document.getElementById("id_id_observador").disabled = true;
      document
        .getElementById("id_observador_externo")
        .removeAttribute("disabled");
        
        document.getElementById("id_observador_externo").setAttribute("required", true)
      } else {
        // document.getElementById("id_id_observador").removeAttribute("disabled");
        document.getElementById("id_observador_externo").disabled = true;
        document.getElementById("id_observador_externo").removeAttribute("required")
    }
  });
