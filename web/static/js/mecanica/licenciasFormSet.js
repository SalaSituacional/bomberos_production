
document.addEventListener('DOMContentLoaded', function () {
const addLicenciaBtn = document.getElementById('add-licencia-form');
const licenciasContainer = document.getElementById('licencias-forms-container');
const licenciaFormTemplate = licenciasContainer.firstElementChild.cloneNode(true); // Clonar el primer formulario como plantilla
const totalForms = document.querySelector('input[name="licencias-TOTAL_FORMS"]');
let formNum = parseInt(totalForms.value);

addLicenciaBtn.addEventListener('click', function () {
    const newForm = licenciaFormTemplate.cloneNode(true);

    // Actualizar todos los atributos name/id con el nuevo índice
    const oldPrefix = 'licencias-0-'; // Asumimos que el primer formulario tiene índice 0 como base
    const newPrefix = `licencias-${formNum}-`;
    const regex = new RegExp(oldPrefix.replace('-', '\\-'), 'g'); // Escapar el guion para la regex

    newForm.innerHTML = newForm.innerHTML.replaceAll(regex, newPrefix);

    // Limpiar valores de los campos clonados
    const inputs = newForm.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
    if (input.type !== 'hidden' && !input.name.includes('DELETE')) {
        if (input.type === 'checkbox' || input.type === 'radio') {
        input.checked = false;
        } else {
        input.value = '';
        }
    }
    });

    // Insertar el nuevo formulario al final del contenedor
    licenciasContainer.appendChild(newForm);

    // Incrementar el contador de formularios
    totalForms.value = formNum + 1;
    formNum++;
});
});