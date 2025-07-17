let botonesVer = document.querySelectorAll(".ver-informacion");
let contenedor = document.getElementById("informacion_unidades");

botonesVer.forEach((boton) => {
  boton.addEventListener("click", async function () {
    let id_unidad = this.getAttribute("data-unidad"); // ID de la unidad

    try {
      const response = await fetchWithLoader(
        `/mecanica/mostrar_informacion/${id_unidad}/`
      );

      let data = await response;


      mostrarInformacion(data);
    } catch (error) {
      contenedor.innerHTML = "";
      console.error("❌ Error al Obtener los Datos:", error);
    }
  });
});

function mostrarInformacion(data) {

  contenedor.scrollIntoView({ behavior: "smooth" });

  contenedor.innerHTML = "";

  contenedor.innerHTML = `
    <div class="Info-Unidades">
        <h2>Informacion de la Unidad</h2>
        
        <div>
            <p><strong>Unidad:</strong> ${data.nombre_unidad}</p>
            <p><strong>Division:</strong> ${data.divisiones[0].division}</p>
        </div>

        <div>
            <p><strong>Tipo de Vehiculo:</strong> ${data.tipo_vehiculo}</p>
            <p><strong>Serial De Carroceria:</strong> ${data.serial_carroceria}</p>
            <p><strong>Serial De Chasis:</strong> ${data.serial_chasis}</p>
        </div>

        <div>
            <p><strong>Marca:</strong> ${data.marca}</p>
            <p><strong>Modelo:</strong> ${data.modelo}</p>
            <p><strong>Año:</strong> ${data.año}</p>
            <p><strong>Placas:</strong> ${data.placas}</p>
        </div>

        <div>
            <p><strong>Tipo de Filtro de Aceite:</strong> ${data.tipo_filtro_aceite}</p>
            <p><strong>Tipo de Filtro de Combustible:</strong> ${data.tipo_filtro_combustible}</p>
            <p><strong>Bateria:</strong> ${data.bateria}</p>
            <p><strong>Numero Tag:</strong> ${data.numero_tag}</p>
            <p><strong>Tipo de Bujia:</strong> ${data.tipo_bujia}</p>
        </div>

        <div>
            <p><strong>Uso:</strong> ${data.uso}</p>
            <p><strong>Capacidad de Carga:</strong> ${data.capacidad_carga}</p>
            <p><strong>Numero de Ejes:</strong> ${data.numero_ejes}</p>
            <p><strong>Numero de Puestos:</strong> ${data.numero_puestos}</p>
        </div>

        <div>
            <p><strong>Tipo de Combustible:</strong> ${data.tipo_combustible}</p>
            <p><strong>Tipo de Aceite:</strong> ${data.tipo_aceite}</p>
            <p><strong>Medida de Neumaticos:</strong> ${data.medida_neumaticos}</p>
            <p><strong>Tipo de Correa:</strong> ${data.tipo_correa}</p>
        </div>

        <div>
            <h4><strong>Estado del Vehiculo:</strong> ${data.estado}</h4>
        </div>
    </div>
  `;

  document.getElementById("reporte_unidades").innerHTML = "";

  // Obtener la referencia a la modal y el botón de confirmación
  const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal2'));
  const confirmDeleteButton = document.getElementById('confirmDeleteButton');

  let reporteIdToDelete = null; // Variable para almacenar el ID del reporte a eliminar

  data.ultimos_reportes.forEach((reporte) => {
      document.getElementById("reporte_unidades").innerHTML += `
      <div class="reporte">
        <div class="reporte-content">
          <h2>Reporte</h2>
          <div>
            <p><strong>Servicio:</strong> ${reporte.servicio}</p>
            <p><strong>Fecha:</strong> ${reporte.fecha}</p>
            <p><strong>Hora:</strong> ${reporte.hora}</p>
          </div>
          <div>
            <p><strong>Descripción:</strong> ${reporte.descripcion}</p>
            <p><strong>Responsable:</strong> ${reporte.persona_responsable}</p>
          </div>
          <button type="button" class="btn btn-danger btn-borrar-reporte" data-reporte-id="${reporte.id}">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </div>
      `;
  });

  // Delegación de eventos: Escuchar clics en los botones de "Eliminar"
  // Esto es importante porque los botones se añaden dinámicamente
  document.getElementById("reporte_unidades").addEventListener('click', (event) => {
      const deleteButton = event.target.closest('.btn-borrar-reporte');
      if (deleteButton) {
          reporteIdToDelete = deleteButton.dataset.reporteId; // Obtiene el ID del reporte
          confirmDeleteModal.show(); // Muestra la modal de confirmación
      }
  });

  // Cuando el usuario hace clic en el botón "Eliminar" dentro de la modal
  confirmDeleteButton.addEventListener('click', async () => {
      if (reporteIdToDelete) {
        // Construye la URL de eliminación con el ID almacenado
        const deleteUrl = DELETE_REPORT_BASE_URL.replace('0', reporteIdToDelete);

        const response = fetchWithLoader(deleteUrl);
        
        if (response) {
          location.reload()
        }

        confirmDeleteModal.hide();
        reporteIdToDelete = null;
      }
  });
}
