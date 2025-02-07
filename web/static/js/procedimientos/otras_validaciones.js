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

eliminarOpciones("id_form2-jefe_comision", "0");
eliminarOpciones("id_form_capacitacion-instructor", "0");

// ==============================================================================================================================================

// Agregar Validacion de Solicitante Externo
var inputExterno = document.getElementById("id_form2-solicitante_externo");

// Luego selecciona el div que es el padre del input
var divContainer = inputExterno.parentElement;

// Ocultar el div
divContainer.style.display = "none";
inputExterno.removeAttribute("required");

document
  .getElementById("id_form2-solicitante")
  .addEventListener("change", function () {
    if (this.value == "0") {
      // Ajusta el valor de "1" según tu lógica
      divContainer.style.display = "flex";
      inputExterno.setAttribute("required", "required");
    } else {
      divContainer.style.display = "none"; // Ocultar solicitante_externo
      inputExterno.removeAttribute("required");
    }
  });

// ====================================================================================================================================================
// Validacion de Municipio, Parroquia
document
  .getElementById("id_form3-municipio")
  .addEventListener("change", function () {
    var select2 = document.getElementById("id_form3-parroquia");

    if (this.value === "1") {
      select2.disabled = false;
      select2.setAttribute("required", "true"); // Elimina el atributo `required`
    } else {
      select2.disabled = true;
      select2.removeAttribute("required"); // Agrega el atributo `required`
    }
  });

// ======================================================================================================================================================
// Validacion Para desabilitar la primera opcion y que no se pueda seleccionar en todos los select 
document.addEventListener("DOMContentLoaded", function () {
    const selects = document.querySelectorAll(".disable-first-option");
    selects.forEach((select) => {
      select.options[0].disabled = true;
    });
  });
  
// =======================================================================================================================================================
// Selecciona todos los inputs de tipo checkbox
const checkboxes = document.querySelectorAll('input[type="checkbox"]');

// Agrega la clase 'checkbox-styles' a cada uno de ellos
checkboxes.forEach((checkbox) => {
checkbox.classList.add("checkbox-styles");

// Selecciona el contenedor padre del checkbox
const parent = checkbox.parentElement; // Cambia esto si el contenedor no es el padre directo
parent.classList.add("flex-row"); // Agrega la clase para aplicar los estilos deseados
});
  