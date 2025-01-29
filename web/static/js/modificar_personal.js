document.querySelectorAll('.edit-button').forEach((button) => {
  button.addEventListener('click', async function () {
    try {
      const id = parseInt(this.getAttribute('data-id')); // Obtener el ID desde el atributo
      if (isNaN(id)) {
        throw new Error('El ID no es válido');
      }

      // Realizar la solicitud con fetchWithLoader
      const response = await fetchWithLoader(`/get_persona/${id}/`);

      // La función fetchWithLoader ya devuelve los datos en JSON, no necesitas volver a procesarlos
      const data = response; 

      let letra, numeros = data.cedula.split("-")

      // Llenar el formulario con los datos obtenidos
      document.getElementById('id_nombres').value = data.nombre || '';
      document.getElementById('id_apellidos').value = data.apellido || '';
      document.getElementById('id_jerarquia').value = data.jerarquia || '';
      document.getElementById('id_cargo').value = data.cargo || '';
      document.getElementById("id_nacionalidad").value = numeros[0] || '';
      document.getElementById("id_cedula").value = parseInt(numeros[1]) || '';
      document.getElementById('id_rol').value = data.rol || '';
      document.getElementById('id_sexo').value = data.sexo || '';
      document.getElementById('id_status').value = data.status || '';
      document.getElementById('id_persona').value = data.id;
      
      if (data.detalles === true) {
        document.getElementById('id_fecha_nacimiento').value = data.fecha_nacimiento;
        document.getElementById('id_fecha_ingreso').value = data.fecha_ingreso;
        document.getElementById('id_talla_camisa').value = data.talla_camisa;
        document.getElementById('id_talla_pantalon').value = data.talla_pantalon;
        document.getElementById('id_talla_zapatos').value = data.talla_zapato;
        document.getElementById('id_grupo_sanguineo').value = data.grupo_sanguineo;
      }

    } catch (error) {
      console.error('Error al obtener persona:', error);
      alert('No se pudo obtener los datos. Por favor, inténtalo de nuevo.');
    }
  });
});
