document.addEventListener("DOMContentLoaded", function () {


// Delegar evento click en el contenedor padre
document.querySelector("tbody").addEventListener("click", async function (event) {
    // Verificar si el clic fue en un botón con la clase "btn-editar"
    if (event.target.classList.contains("btn-editar")) {
        const id = event.target.getAttribute("data-id");

        try {
            // Llamada a fetchWithLoader para cargar datos del procedimiento
            const data = await fetchWithLoader(`/api/obtener_informacion/${id}/`);
            // const data = await fetchWithLoader(`/api/obtener_informacion/149/`);

            // Guardar la información en localStorage
            localStorage.setItem('fetchedData', JSON.stringify(data));

            // Redirigir a la página destino
            window.location.href = '/editar_procedimientos/';

        } catch (err) {
            alert("Hubo un problema al cargar los datos.");
        }
    }
});

// // Enviar los datos del formulario
// const form = document.getElementById("editar-form");
// form.addEventListener("submit", async function (event) {
//     event.preventDefault();

//     // Obtener los valores del formulario, incluidas las comisiones
//     const formData = new FormData(form);
//     const jsonData = Object.fromEntries(formData.entries());

//     // Obtener el ID del procedimiento
//     const id = document.getElementById("editar-id").value;

//     try {
//         // Llamada a fetchWithLoader para enviar los datos al servidor
//         await fetchWithLoader(`/editar_procedimiento/${id}/`, {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": getCSRFToken(),
//             },
//             body: JSON.stringify(jsonData),
//         });
//         location.reload(); // Recargar la página para reflejar los cambios
//     } catch (err) {
//         alert("Hubo un problema al guardar los cambios.");
//     }
// });

// // Obtener el token CSRF
// function getCSRFToken() {
//     const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
//     return csrfToken;
// }
});




// function generateComisionForms(comisiones) {
    //     const comisionContainer = document.getElementById("comision-fields");
    //     comisionContainer.innerHTML = ""; // Limpiar el contenedor

    //     comisiones.forEach((comision, index) => {
    //         const comisionFormHTML = `
    //             <div class="comision-form" id="comision-${index}">
    //                 <h4>Comisión ${index + 1}</h4>
    //                 <div class="form-group">
    //                     <label for="tipo_comision-${index}">Tipo de Comisión</label>
    //                     <input type="text" id="tipo_comision-${index}" name="comisiones[${index}][tipo_comision]" value="${comision.tipo_comision || ""}" />
    //                 </div>
    //                 <div class="form-group">
    //                     <label for="nombre_oficial-${index}">Nombre del Oficial</label>
    //                     <input type="text" id="nombre_oficial-${index}" name="comisiones[${index}][nombre_oficial]" value="${comision.nombre_oficial || ""}" />
    //                 </div>
    //                 <div class="form-group">
    //                     <label for="apellido_oficial-${index}">Apellido del Oficial</label>
    //                     <input type="text" id="apellido_oficial-${index}" name="comisiones[${index}][apellido_oficial]" value="${comision.apellido_oficial || ""}" />
    //                 </div>
    //                 <div class="form-group">
    //                     <label for="cedula_oficial-${index}">Cédula del Oficial</label>
    //                     <input type="text" id="cedula_oficial-${index}" name="comisiones[${index}][cedula_oficial]" value="${comision.cedula_oficial || ""}" />
    //                 </div>
    //                 <div class="form-group">
    //                     <label for="nro_unidad-${index}">Número de Unidad</label>
    //                     <input type="text" id="nro_unidad-${index}" name="comisiones[${index}][nro_unidad]" value="${comision.nro_unidad || ""}" />
    //                 </div>
    //                 <div class="form-group">
    //                     <label for="nro_cuadrante-${index}">Número de Cuadrante</label>
    //                     <input type="text" id="nro_cuadrante-${index}" name="comisiones[${index}][nro_cuadrante]" value="${comision.nro_cuadrante || ""}" />
    //                 </div>
    //                 <hr />
    //             </div>
    //         `;
    //         comisionContainer.insertAdjacentHTML("beforeend", comisionFormHTML);
    //     });
    // }

    // Generar campos dinámicos según el tipo de procedimiento
    // function generateDynamicFields(data) {
    //     const dynamicContainer = document.getElementById("dynamic-fields");
    //     let dynamicHTML = "";

    //     switch (data.id_tipo_procedimiento) {
    //         case 1: // Abastecimiento de agua
    //             dynamicHTML = `
    //                 <div class="form-group">
    //                     <label for="editar-litros-agua">Litros de Agua</label>
    //                     <input type="number" id="editar-litros-agua" name="ltrs_agua" value="${data.ltrs_agua || 0}" />
    //                 </div>
    //                 <div class="form-group">
    //                     <label for="editar-nombres">Nombres</label>
    //                     <input type="text" id="editar-nombres" name="nombres" value="${data.nombres || ""}" />
    //                 </div>
    //                 <div class="form-group">
    //                     <label for="editar-apellidos">Apellidos</label>
    //                     <input type="text" id="editar-apellidos" name="apellidos" value="${data.apellidos || ""}" />
    //                 </div>
    //             `;
    //             break;

    //         case 2: // Apoyo a Unidades
    //             dynamicHTML = `
    //                 <div class="form-group">
    //                     <label for="editar-tipo-apoyo">Tipo de Apoyo</label>
    //                     <input type="text" id="editar-tipo-apoyo" name="tipo_apoyo" value="${data.tipo_apoyo || ""}" />
    //                 </div>
    //                 <div class="form-group">
    //                     <label for="editar-unidad-apoyada">Unidad Apoyada</label>
    //                     <input type="text" id="editar-unidad-apoyada" name="unidad_apoyada" value="${data.unidad_apoyada || ""}" />
    //                 </div>
    //             `;
    //             break;

    //         case 3: // Guardia de Prevención
    //             dynamicHTML = `
    //                 <div class="form-group">
    //                     <label for="editar-motivo-prevencion">Motivo de Prevención</label>
    //                     <input type="text" id="editar-motivo-prevencion" name="motivo_prevencion" value="${data.motivo_prevencion || ""}" />
    //                 </div>
    //             `;
    //             break;

    //         default:
    //             dynamicHTML = `<p>No se han definido campos adicionales para este tipo de procedimiento.</p>`;
    //     }

    //     // Insertar los campos dinámicos en el contenedor del formulario
    //     dynamicContainer.innerHTML = dynamicHTML;
    // }