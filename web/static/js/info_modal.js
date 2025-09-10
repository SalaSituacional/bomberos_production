// Delegar eventos al contenedor padre
const info_modal = document.getElementById("info_modal");

document.addEventListener("DOMContentLoaded", function () {
  const tbodyContainer = document.querySelector("tbody");

if (tbodyContainer) {
  tbodyContainer.addEventListener("click", async function (event) {
    // Verificar si se hizo clic en un botón de acción
    if (event.target && (event.target.matches(".button_delete") || event.target.matches(".btn-editar") || event.target.closest(".button_delete") || event.target.closest(".btn-editar"))) {
        return; // No hacer nada si es un botón de acción
    }

    // Encontrar la fila clickeada
    const targetRow = event.target.closest('tr');
    if (!targetRow) return;
    
    const id = targetRow.getAttribute('data-id');
    const id_tipo_procedimiento = targetRow.getAttribute("data-id_procedimiento");
    
    info_modal.textContent = ""; // Limpiar contenido del modal

    const modalProcedimiento = new bootstrap.Modal(document.getElementById('modal-info'));
    modalProcedimiento.show();

      try {
        const data = await fetchWithLoader(`/api/procedimientos/${id}/`);

        let baseInfo = "";
        let solicitante;
        if (data.solicitante_externo == "") {
          solicitante = data.solicitante;
        } else {
          solicitante = data.solicitante_externo;
        }
        let division = data.division;
        if (
          division == "Rescate" ||
          division == "Operaciones" ||
          division == "Prevencion" ||
          division == "GRUMAE" ||
          division == "PreHospitalaria"
        ) {
          baseInfo = ` 
                <article class="section-left">
                <h4>Division</h4>
                <section class="datos_division">
                  <p><b>Division: </b> ${data.division}</p>
                  <p><b>ID Procedimiento: </b> #${data.id}</p>
                </section>
                <h4>Operacion</h4>
                <section class="datos_operacion">
                  <p><b>Solicitante: </b> ${solicitante}</p>
                  <p><b>Jefe de Comision: </b> ${data.jefe_comision}</p>
                  <p><b>Unidad Enviada: </b> ${data.unidad}</p>
                  <p><b>Efectivos Enviados: </b> ${data.efectivos}</p>
                </section>
                <h4>Ubicacion</h4>
                <section class="datos_ubicacion">
                  <p><b>Parroquia: </b> ${data.parroquia}</p>
                  <p><b>Municipio: </b> ${data.municipio}</p>
                  <p><b>Direccion: </b> ${data.direccion}</p>
                  <p><b>Fecha: </b> ${data.fecha}</p>
                  <p><b>Hora: </b> ${data.hora}</p>
                </section>`;
          if (data.comisiones && data.comisiones.length > 0) {
            baseInfo += `
                        
                      `;

            // Iterar sobre cada comisión y agregar su contenido
            data.comisiones.forEach((comision, index) => {
              baseInfo += `
                        <h4>Comision Presente ${index + 1}</h4>
                        <section class="datos_comisiones">
                            <p><b>Tipo de Comisión: </b> ${comision.comision}</p>
                            <p><b>Nombre del Oficial: </b> ${
                              comision.nombre_oficial
                            } ${comision.apellido_oficial}</p>
                            <p><b>Cédula del Oficial: </b> ${
                              comision.cedula_oficial
                            }</p>
                            <p><b>Número de Unidad: </b> ${
                              comision.nro_unidad
                            }</p>
                            <p><b>Número de Cuadrante: </b> ${
                              comision.nro_cuadrante
                            }</p>
                          </section>
                        `;
            });
          }
        }
        if (division == "Enfermeria") {
          baseInfo = ` 
            <article class="section-left">
                  <h4>Division</h4>
                  <section class="datos_division">
                    <p><b>Division: </b> ${data.division}</p>
                    <p><b>ID Procedimiento: </b> #${data.id}</p>
                  </section>
                  <h4>Operacion</h4>
                  <section class="datos_operacion">
                    <p><b>Dependencia: </b> ${data.dependencia}</p>
                    <p><b>Jefe de Area: </b> ${solicitante}</p>
                    </section>
                    <h4>Ubicacion</h4>
                    <section class="datos_ubicacion">
                    <p><b>Parroquia: </b> ${data.parroquia}</p>
                    <p><b>Municipio: </b> ${data.municipio}</p>
                    <p><b>Direccion: </b> ${data.direccion}</p>
                    <p><b>Fecha: </b> ${data.fecha}</p>
                    <p><b>Hora: </b> ${data.hora}</p>
                    </section>`;
        }
        if (division == "Servicios Medicos") {
          baseInfo = ` 
                <article class="section-left">
                <h4>Division</h4>
                  <section class="datos_division">
                    <p><b>Division: </b> ${data.division}</p>
                    <p><b>ID Procedimiento: </b> #${data.id}</p>
                    </section>
                    <h4>Operacion</h4>
                    <section class="datos_operacion">
                    <p><b>Tipo de Servicio: </b> ${data.tipo_servicio}</p>
                    <p><b>Jefe de Area: </b> ${solicitante}</p>
                    </section>
                    <h4>Ubicacion</h4>
                    <section class="datos_ubicacion">
                    <p><b>Parroquia: </b> ${data.parroquia}</p>
                    <p><b>Municipio: </b> ${data.municipio}</p>
                    <p><b>Direccion: </b> ${data.direccion}</p>
                    <p><b>Fecha: </b> ${data.fecha}</p>
                    <p><b>Hora: </b> ${data.hora}</p>
                    </section>`;
        }
        if (division == "Psicologia") {
          baseInfo = ` 
                <article class="section-left">
                <h4>Division</h4>
                  <section class="datos_division">
                    <p><b>Division: </b> ${data.division}</p>
                    <p><b>ID Procedimiento: </b> #${data.id}</p>
                    <p><b>Jefe de Area: </b> ${solicitante}</p>
                    </section>
                    <h4>Ubicacion</h4>
                    <section class="datos_ubicacion">
                    <p><b>Parroquia: </b> ${data.parroquia}</p>
                    <p><b>Municipio: </b> ${data.municipio}</p>
                    <p><b>Direccion: </b> ${data.direccion}</p>
                    <p><b>Fecha: </b> ${data.fecha}</p>
                    <p><b>Hora: </b> ${data.hora}</p>
                    </section>`;
        }
        if (division == "Capacitacion") {
          baseInfo = ` 
                <article class="section-left">
                <h4>Division</h4>
                  <section class="datos_division">
                    <p><b>Division: </b> ${data.division}</p>
                    <p><b>ID Procedimiento: </b> #${data.id}</p>
                    </section>
                    <h4>Operacion</h4>
                    <section class="datos_operacion">
                    <p><b>Solicitante: </b> ${solicitante}</p>
                    <p><b>Instructor: </b> ${data.jefe_comision}</p>
                    <p><b>Dependencia: </b> ${data.dependencia}</p>
                    </section>
                    <h4>Ubicacion</h4>
                    <section class="datos_ubicacion">
                    <p><b>Parroquia: </b> ${data.parroquia}</p>
                    <p><b>Municipio: </b> ${data.municipio}</p>
                    <p><b>Direccion: </b> ${data.direccion}</p>
                    <p><b>Fecha: </b> ${data.fecha}</p>
                    <p><b>Hora: </b> ${data.hora}</p>
                    </section>`;
        }
        let detalles = "";

        // Estructura if-else para manejar cada tipo de procedimiento
        switch (id_tipo_procedimiento) {
          case "Abastecimiento de agua":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(data, "ente_suministrado")}
                  </section>
                  <h4>Comunidad</h4>
                  <section>
                  <p><b>Personas Atendidas: </b> ${data.personas_atendidas}</p>
                  <p><b>Nombre Persona Presente: </b> ${data.nombres}</p>
                  <p><b>Apellidos Persona Presente: </b> ${data.apellidos}</p>
                  <p><b>Cedula Persona Presente: </b> ${data.cedula}</p>
                  <p><b>Litros de Agua Suministrada: </b> ${data.ltrs_agua} L</p>
                  </section>`;
            break;
          case "Apoyo a Otras Unidades":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
                    ${generateCommonDetails(data, "tipo_apoyo", "unidad_apoyada")}
                  </section>`;
            break;
          case "Guardia de Prevencion":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
                    ${generateCommonDetails(data, "motivo_prevencion")}
                    </section>`;
            break;
          case "Atendido No Efectuado":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    ${generateCommonDetails(data)}
                  </section> 
                  `;
            break;
          case "Despliegue de Seguridad":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    ${generateCommonDetails(data, "motivo_despliegue")}
                  </section>`;
            break;
          case "Falsa Alarma":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(data, "motivo_alarma")}
                  </section> 
                  `;
            break;
          case "Atenciones Paramedicas":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    <p><b>Tipo de Procedimiento: </b> ${data.tipo_procedimiento}</p>
                    <p><b>Tipo de Atencion: </b> ${data.tipo_atencion}</p>
                  `;
            if (data.emergencia) {
              detalles += `
                    </section>
                    <h4>Atendido</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Nombres: </b> ${data.nombres}</p>
                    <p><b>Apellidos: </b> ${data.apellidos}</p>
                    <p><b>Cedula: </b> ${data.cedula}</p>
                    <p><b>Edad: </b> ${data.edad}</p>
                    <p><b>Sexo: </b> ${data.sexo}</p>
                    </section>
                    <h4>Emergencia</h4>
                    <section class="detalles_procedimiento">
                    <p><b>IDX: </b> ${data.idx}</p>
                    <p><b>Descripcion: </b> ${data.descripcion}</p>
                    <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                    <p><b>Status: </b> ${data.status}</p>
                    </section>`;
              if (data.traslado) {
                detalles += `
                <h4>Traslado</h4>
                      <section class="detalles_procedimiento">
                        <p><b>Hospital: </b> ${data.hospital}</p>
                        <p><b>Medico: </b> ${data.medico}</p>
                        <p><b>MPPS CMT: </b> ${data.mpps_cmt}</p>
                        </section>`;
              }
            }
            if (data.accidente) {
              detalles += `
                    <p><b>Tipo de Accidente: </b> ${data.tipo_accidente}</p>
                    <p><b>Cantidad Lesionados: </b> ${data.cantidad_lesionados}</p>
                    <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                    <p><b>Status: </b> ${data.status}</p>
                  </section>`;

              // Verificamos si hay vehículos
              if (data.vehiculos && data.vehiculos.length > 0) {
                data.vehiculos.forEach((vehiculo, index) => {
                  // Creamos una sección para cada vehículo
                  detalles += `
                  <h4>Vehículo ${index + 1}</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Marca:</b> ${vehiculo.marca}</p>
                    <p><b>Modelo:</b> ${vehiculo.modelo}</p>
                    <p><b>Color:</b> ${vehiculo.color}</p>
                    <p><b>Año:</b> ${vehiculo.año}</p>
                          <p><b>Placa:</b> ${vehiculo.placas}</p>
                        </section>`;
                });
              } else {
              }

              // Verificamos si hay lesionados
              if (data.lesionados && data.lesionados.length > 0) {
                data.lesionados.forEach((lesionado, index) => {
                  // Creamos una sección para cada lesionado
                  detalles += `
                  <h4>Lesionado ${index + 1}</h4>
                    <section class="detalles_lesionados">
                    <p><b>Nombre:</b> ${lesionado.nombre}</p>
                    <p><b>Apellidos:</b> ${lesionado.apellidos}</p>
                    <p><b>Cedula:</b> ${lesionado.cedula}</p>
                    <p><b>Edad:</b> ${lesionado.edad}</p>
                    <p><b>Sexo:</b> ${lesionado.sexo}</p>
                    <p><b>IDX:</b> ${lesionado.idx}</p>
                    <p><b>Descripción:</b> ${lesionado.descripcion}</p>
                    `;
                  // Verificamos si el lesionado tiene traslados asociados
                  if (lesionado.traslados && lesionado.traslados.length > 0) {
                    lesionado.traslados.forEach((traslado, trasladoIndex) => {
                      // Añadimos una sub-sección para cada traslado
                      detalles += `
                        <h4><b>Traslado</b></h4>
                        <p><b>Hospital:</b> ${traslado.hospital}</p>
                        <p><b>Médico receptor:</b> ${traslado.medico}</p>
                        <p><b>MPPS CMT:</b> ${traslado.mpps_cmt}</p>
                          </section>`;
                    });
                  } else {
                    detalles += `</section>`;
                  }
                });
              } else {
              }
            }
            break;
          case "Servicios Especiales":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    ${generateCommonDetails(data, "tipo_servicio")}
                  </section>`;
            break;
          case "Rescate":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    <p><b>Tipo de Procedimiento: </b> ${data.tipo_procedimiento}</p>
                    <p><b>Tipo de Rescate: </b> ${data.tipo_rescate}</p>
                    <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                    <p><b>Status: </b> ${data.status}</p>
                  </section>
                  `;
            if (data.tipo_rescate === "Rescate de Animal") {
              detalles += `
              <h4>Animal</h4>
                <section class="detalles_rescate_animal">
                <p><b>Especie: </b> ${data.especie}</p>
                <p><b>Descripcion: </b> ${data.descripcion}</p>
                </section>
                `;
            } else {
              detalles += `
              <h4>Persona</h4>
                    <section class="detalles_rescate_persona">
                      <p><b>Nombre: </b> ${data.nombres}</p>
                      <p><b>Apellido: </b> ${data.apellidos}</p>
                      <p><b>Cedula: </b> ${data.cedula}</p>
                      <p><b>Edad: </b> ${data.edad}</p>
                      <p><b>Sexo: </b> ${data.sexo}</p>
                      <p><b>Descripcion: </b> ${data.descripcion}</p>
                      </section>`;
            }

            break;
          case "Incendios":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    ${generateCommonDetails(data, "tipo_incendio")}
                    </section>
                    ${
                      data.persona
                        ? `
                        <h4>Persona en el Sitio</h4>
                    <section class="detalles_persona_sitio">
                      <p><b>Nombre: </b> ${data.nombre}</p>
                      <p><b>Apellido: </b> ${data.apellidos}</p>
                      <p><b>Cedula: </b> ${data.cedula}</p>
                      <p><b>Telefono: </b> ${data.edad}</p>
                      </section>`
                        : ""
                    }
                    ${
                      data.retencion
                        ? `
                          <h4>Datos del Cilindro</h4>
                          <section class="detalles_procedimiento">
                          <p><b>Tipo de Cilindro: </b> ${data.tipo_cilindro}</p>
                          <p><b>Capacidad: </b> ${data.capacidad}</p>
                          <p><b>serial: </b> ${data.serial}</p>
                          <p><b>Numero de Constancia de Retencion: </b>#${
                            data.nro_constancia
                          }</p>
                          <p><b>Nombre de la Persona: </b>${data.nombre}</p>
                          <p><b>Apellido de la Persona: </b>${data.apellidos}</p>
                          <p><b>Cedula de la Persona: </b>${data.cedula}</p>
                          </section>`
                          : ""
                    }
                      ${
                        data.vehiculo
                          ? `
                          <h4>Vehiculo</h4>
                    <section class="detalles_vehiculo">
                      <p><b>Modelo: </b> ${data.modelo}</p>
                      <p><b>Marca: </b> ${data.marca}</p>
                      <p><b>Color: </b> ${data.color}</p>
                      <p><b>Año: </b> ${data.año}</p>
                      <p><b>Placas: </b> ${data.placas}</p>
                      </section>`
                          : ""
                      }`;
            break;
          case "Fallecidos":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
                    ${generateCommonDetails(data, "motivo_fallecimiento")}
                    </section>
                    <h4>Fallecido</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Nombre: </b> ${data.nombres}</p>
                    <p><b>Apellido: </b> ${data.apellidos}</p>
                    <p><b>Cedula: </b> ${data.cedula}</p>
                    <p><b>Edad: </b> ${data.edad}</p>
                    <p><b>Sexo: </b> ${data.sexo}</p>
                    </section>`;
            break;
          case "Mitigación de Riesgos":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(data, "tipo_servicio")}
                  </section>`;
            // Verificamos si hay vehículos
            if (data.vehiculos && data.vehiculos.length > 0) {
              data.vehiculos.forEach((vehiculo, index) => {
                // Creamos una sección para cada vehículo
                detalles += `
                <h4>Vehículo ${index + 1}</h4>
                <section class="detalles_procedimiento">
                  <p><b>Marca:</b> ${vehiculo.marca}</p>
                  <p><b>Modelo:</b> ${vehiculo.modelo}</p>
                  <p><b>Color:</b> ${vehiculo.color}</p>
                  <p><b>Año:</b> ${vehiculo.año}</p>
                  <p><b>Placa:</b> ${vehiculo.placas}</p>
                </section>`;
              });
            } else {
            }

            break;
          case "Puesto de Avanzada":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
              ${generateCommonDetails(data, "tipo_de_servicio")}
                          </section>`;
            break;
          case "Evaluación de Riesgos":
            if (data.tipo_estructura) {
              if (data.division == "Prevencion") {
                detalles = `
                <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(
                    data,
                    "tipo_de_evaluacion",
                    "tipo_estructura"
                  )}
                  </section>
                  <h4>Persona Presente</h4>
                  <section class="detalles_procedimiento">
                  <p><b>Nombre: </b> ${data.nombre}</p>
                  <p><b>Apellido: </b> ${data.apellido}</p>
                  <p><b>Cedula: </b> ${data.cedula}</p>
                  <p><b>Telefono: </b> ${data.telefono}</p>
                  </section>`;
              } else {
                detalles = `
                <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(
                    data,
                    "tipo_de_evaluacion",
                    "tipo_estructura"
                  )}
                  </section>`;
              }
            } else {
              if (data.division == "Prevencion") {
                detalles = `
                <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    ${generateCommonDetails(data, "tipo_de_evaluacion")}
                    </section>
                    <h4>Persona Presente</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Nombre: </b> ${data.nombre}</p>
                    <p><b>Apellido: </b> ${data.apellido}</p>
                    <p><b>Cedula: </b> ${data.cedula}</p>
                    <p><b>Telefono: </b> ${data.telefono}</p>
                    </section>`;
              } else {
                detalles = `
                <h4>Detalles</h4>
                    <section class="detalles_procedimiento">
                    ${generateCommonDetails(data, "tipo_de_evaluacion")}
                    </section>`;
              }
            }
            break;
          case "Asesoramiento":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
                    ${generateCommonDetails(data)}
                    </section>
                    <h4>Informacion del Comercio</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Nombre del Comercio: </b> ${data.nombre_comercio}</p>
                    <p><b>RIF del Comercio: </b> ${data.rif_comercio}</p>
                    </section>
                    <h4>Persona Solicitante</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Nombre: </b> ${data.nombre}</p>
                    <p><b>Apellido: </b> ${data.apellido}</p>
                    <p><b>Cedula: </b> ${data.cedula}</p>
                    <p><b>Sexo: </b> ${data.sexo}</p>
                    <p><b>Telefono: </b> ${data.telefono}</p>
                    </section>`;
            break;
          case "Inspeccion":
            switch (data.tipo_inspeccion) {
              case "Prevención":
                detalles += `
                <h4>Detalles</h4>
                    <section class="detalles_procedimiento">
                        ${generateCommonDetails(data, "tipo_inspeccion")}
                        </section>
                        <h4>Información del Comercio</h4>
                        <section class="detalles_procedimiento">
                        <p><b>Nombre del Comercio: </b> ${
                          data.nombre_comercio
                        }</p>
                        <p><b>Propietario: </b> ${data.propietario}</p>
                        <p><b>Cédula del Propietario: </b> ${
                          data.cedula_propietario
                        }</p>
                          </section>
                          <h4>Persona en el Sitio</h4>
                          <section class="detalles_procedimiento">
                        <p><b>Nombre: </b> ${data.persona_sitio_nombre}</p>
                        <p><b>Apellido: </b> ${data.persona_sitio_apellido}</p>
                        <p><b>Cédula: </b> ${data.persona_sitio_cedula}</p>
                        <p><b>Teléfono: </b> ${data.persona_sitio_telefono}</p>
                        </section>`;
                break;

              case "Asesorias Tecnicas":
                detalles += `
                <h4>Detalles</h4>
                    <section class="detalles_procedimiento">
                        ${generateCommonDetails(data, "tipo_inspeccion")}
                    </section>
                    <h4>Información del Comercio</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Nombre del Comercio: </b> ${data.nombre_comercio}</p>
                        <p><b>Propietario: </b> ${data.propietario}</p>
                        <p><b>Cédula del Propietario: </b> ${
                          data.cedula_propietario
                        }</p>
                          </section>
                          <h4>Persona en el Sitio</h4>
                          <section class="detalles_procedimiento">
                        <p><b>Nombre: </b> ${data.persona_sitio_nombre}</p>
                        <p><b>Apellido: </b> ${data.persona_sitio_apellido}</p>
                        <p><b>Cédula: </b> ${data.persona_sitio_cedula}</p>
                        <p><b>Teléfono: </b> ${data.persona_sitio_telefono}</p>
                        </section>`;
                break;

              case "Habitabilidad":
                detalles += `
                <h4>Detalles</h4>
                    <section class="detalles_procedimiento">
                        ${generateCommonDetails(data, "tipo_inspeccion")}
                        </section>
                        <h4>Persona en el Sitio</h4>
                        <section class="detalles_procedimiento">
                        <p><b>Nombre: </b> ${data.persona_sitio_nombre}</p>
                        <p><b>Apellido: </b> ${data.persona_sitio_apellido}</p>
                        <p><b>Cédula: </b> ${data.persona_sitio_cedula}</p>
                        <p><b>Teléfono: </b> ${data.persona_sitio_telefono}</p>
                    </section>`;
                break;

              case "Otros":
                detalles += `
                <h4>Procedimiento</h4>
                    <section class="detalles_procedimiento">
                        <p><b>Tipo de Procedimiento: </b> ${data.tipo_procedimiento}</p>
                        <p><b>Tipo de Inspeccion: </b> ${data.tipo_inspeccion}</p>
                        <p><b>Especifique: </b> ${data.especifique}</p>
                      </section>
                      <h4>Detalles</h4>
                      <section class="detalles_procedimiento">
                        <p><b>Descripcion: </b> ${data.descripcion}</p>
                        <p><b>Materia Utilizado: </b> ${data.material_utilizado}</p>
                        <p><b>Status: </b> ${data.status}</p>
                        </section>
                        <h4>Persona en el Sitio</h4>
                        <section class="detalles_procedimiento">
                        <p><b>Nombre: </b> ${data.persona_sitio_nombre}</p>
                        <p><b>Apellido: </b> ${data.persona_sitio_apellido}</p>
                        <p><b>Cédula: </b> ${data.persona_sitio_cedula}</p>
                        <p><b>Teléfono: </b> ${data.persona_sitio_telefono}</p>
                        </section>`;
                break;

              case "Árbol":
                detalles += `
                <h4>Detalles</h4>
                          <section class="detalles_procedimiento">
                        ${generateCommonDetails(data, "tipo_inspeccion")}
                    </section>
                    <h4>Detalles del Árbol</h4>
                    <section class="detalles_procedimiento">
                        <p><b>Especie: </b> ${data.especie}</p>
                        <p><b>Altura Aproximada: </b> ${data.altura_aprox}</p>
                        <p><b>Ubicación: </b> ${data.ubicacion_arbol}</p>
                        </section>
                        <h4>Persona en el Sitio</h4>
                        <section class="detalles_procedimiento">
                        <p><b>Nombre: </b> ${data.persona_sitio_nombre}</p>
                        <p><b>Apellido: </b> ${data.persona_sitio_apellido}</p>
                        <p><b>Cédula: </b> ${data.persona_sitio_cedula}</p>
                        <p><b>Teléfono: </b> ${data.persona_sitio_telefono}</p>
                        </section>`;
                break;

              default:
                detalles += `<p>No se encontraron detalles para este tipo de inspección.</p>`;
            }

            break;
          case "Investigacion":
            detalles = `
            <h4>Informacion De Detalles</h4>
                  <section class="detalles_procedimiento">
                      <p><b>Tipo de Procedimiento: </b> ${data.tipo_procedimiento}</p>
                      <p><b>Tipo de Investigacion: </b> ${data.tipo_investigacion}</p>
                      <p><b>Tipo Siniestro: </b> ${data.tipo_siniestro}</p>
                      </section>
                      `;
            switch (data.tipo_siniestro) {
              case "Vehiculo":
                detalles += `
                <h4>Detalles del Vehículo</h4>
                          <section class="detalles_procedimiento">
                          <p><b>Marca: </b> ${data.marca}</p>
                          <p><b>Modelo: </b> ${data.modelo}</p>
                          <p><b>Color: </b> ${data.color}</p>
                          <p><b>Placas: </b> ${data.placas}</p>
                          <p><b>Año: </b> ${data.año}</p>
                          </section>
                          <h4>Información del Propietario</h4>
                          <section class="detalles_procedimiento">
                          <p><b>Nombre: </b> ${data.nombre_propietario}</p>
                          <p><b>Apellido: </b> ${data.apellido_propietario}</p>
                          <p><b>Cedula: </b> ${data.cedula_propietario}</p>
                          </section>
                          <section class="detalles_procedimiento">
                            <h4>Descripción</h4>
                            <p><b>Descripcion: </b> ${data.descripcion}</p>
                            <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                            <p><b>Status: </b> ${data.status}</p>
                            </section>`;
                break;

              case "Comercio":
                detalles += `
                <h4>Información del Comercio</h4>
                          <section class="detalles_procedimiento">
                            <p><b>Nombre del Comercio: </b> ${data.nombre_comercio_investigacion}</p>
                            <p><b>RIF del Comercio: </b> ${data.rif_comercio_investigacion}</p>
                          </section>
                          <h4>Información del Propietario</h4>
                          <section class="detalles_procedimiento">
                            <p><b>Nombre: </b> ${data.nombre_propietario_comercio}</p>
                            <p><b>Apellido: </b> ${data.apellido_propietario_comercio}</p>
                            <p><b>Cedula: </b> ${data.cedula_propietario_comercio}</p>
                            </section>
                            <h4>Descripción</h4>
                            <section class="detalles_procedimiento">
                            <p><b>Descripcion: </b> ${data.descripcion_comercio}</p>
                            <p><b>Material Utilizado: </b> ${data.material_utilizado_comercio}</p>
                            <p><b>Status: </b> ${data.status_comercio}</p>
                            </section>`;
                break;

              case "Estructura":
                detalles += `
                <h4>Información</h4>
                          <section class="detalles_procedimiento">
                            <p><b>Tipo de Estructura: </b> ${data.tipo_estructura}</p>
                            <p><b>Nombre: </b> ${data.nombre_propietario_estructura}</p>
                            <p><b>Apellido: </b> ${data.apellido_propietario_estructura}</p>
                            <p><b>Cedula: </b> ${data.cedula_propietario_estructura}</p>
                          </section>
                          <h4>Descripción</h4>
                          <section class="detalles_procedimiento">
                            <p><b>Descipcion: </b> ${data.descripcion_estructura}</p>
                            <p><b>Material Utilizado: </b> ${data.material_utilizado_estructura}</p>
                            <p><b>Status: </b> ${data.status_estructura}</p>
                            </section>`;
                break;

              case "Vivienda":
                detalles += `
                <h4>Información</h4>
                          <section class="detalles_procedimiento">
                          <p><b>Tipo de Vivienda: </b> ${data.tipo_estructura}</p>
                            <p><b>Nombre: </b> ${data.nombre_propietario_estructura}</p>
                            <p><b>Apellido: </b> ${data.apellido_propietario_estructura}</p>
                            <p><b>Cedula: </b> ${data.cedula_propietario_estructura}</p>
                          </section>
                          <h4>Descripción</h4>
                          <section class="detalles_procedimiento">
                            <p><b>Descripcion: </b> ${data.descripcion_estructura}</p>
                            <p><b>Material Utilizado: </b> ${data.material_utilizado_estructura}</p>
                            <p><b>Status: </b> ${data.status_estructura}</p>
                            </section>`;
                break;
            }
            break;
          case "Reinspeccion de Prevención":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    ${generateCommonDetails(data)}
                  </section>
                  <h4>Informacion del Comercio</h4>
                  <section class="detalles_procedimiento">
                    <p><b>Nombre del Comercio: </b> ${data.nombre_comercio}</p>
                    <p><b>Rif del Comercio: </b> ${data.rif_comercio}</p>
                    </section>
                    <h4>Persona Solicitante</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Nombre: </b> ${data.nombre}</p>
                    <p><b>Apellido: </b> ${data.apellido}</p>
                    <p><b>Cedula: </b> ${data.cedula}</p>
                    <p><b>Sexo: </b> ${data.sexo}</p>
                    <p><b>Telefono: </b> ${data.telefono}</p>
                  </section>`;
            break;
          case "Retención Preventiva":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                    ${generateCommonDetails(data)}
                    </section>
                    <h4>Datos del Cilindro</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Tipo de Cilindro: </b> ${data.tipo_cilindro}</p>
                    <p><b>Capacidad: </b> ${data.capacidad}</p>
                    <p><b>serial: </b> ${data.serial}</p>
                    <p><b>Numero de Constancia de Retencion: </b>#${
                      data.nro_constancia
                    }</p>
                    <p><b>Nombre de la Persona: </b>${data.nombre}</p>
                    <p><b>Apellido de la Persona: </b>${data.apellidos}</p>
                    <p><b>Cedula de la Persona: </b>${data.cedula}</p>
                      </section>`;
            break;
          case "Traslados":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(data, "traslado")}
                  </section>
                  <h4>Persona Trasladada</h4>
                  <section class="detalles_procedimiento">
                    <p><b>Nombre: </b> ${data.nombre}</p>
                    <p><b>Apellido: </b> ${data.apellido}</p>
                    <p><b>Cedula: </b> ${data.cedula}</p>
                    <p><b>Edad: </b> ${data.edad}</p>
                    <p><b>Sexo: </b> ${data.sexo}</p>
                    <p><b>idx: </b> ${data.idx}</p>
                    </section>
                    <h4>Hospital De Traslado</h4>
                    <section class="detalles_procedimiento">
                    <p><b>Hospital: </b> ${data.hospital}</p>
                    <p><b>Medico Receptor: </b> ${data.medico}</p>
                    <p><b>MPPS CMT: </b> ${data.mpps}</p>
                    </section>`;
            break;
          case "Artificios Pirotécnicos":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
              <p><b>Tipo De Procedimiento: </b> ${data.tipo_procedimiento}</p>
              <p><b>Tipo de Procedimiento Por Artificio: </b> ${data.tipo_procedimiento_art}</p>
                <p><b>Nombre del Distribuidor: </b> ${data.nombre_comercio}</p>
                <p><b>RIF Del Distribuidor: </b> ${data.rif_comercio}</p>
                </section>`;

            if (
              data.tipo_procedimiento_art === "Incendio por Artificio Pirotecnico"
            ) {
              detalles += `
              <h4>Informacion del Incendio</h4>
                <section class="detalles_procedimiento">
                <p><b>Tipo De Incendio: </b> ${data.tipo_incendio}</p>
                  <p><b>Descripcion: </b> ${data.descripcion}</p>
                  <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                  <p><b>Status: </b> ${data.status}</p>
                </section>`;
              if (data.person == true) {
                detalles += `
                <h4>Persona Presente</h4>
                  <section class="detalles_procedimiento">
                  <p><b>Nombre: </b> ${data.nombre}</p>
                  <p><b>Apellido: </b> ${data.apellidos}</p>
                  <p><b>Cedula: </b> ${data.cedula}</p>
                  <p><b>Edad: </b> ${data.edad}</p>
                  </section>`;
              }
              if (data.carro == true) {
                detalles += `
                <h4>Datos del Vehiculo</h4>
                  <section class="detalles_procedimiento">
                  <p><b>Modelo: </b> ${data.modelo}</p>
                  <p><b>Marca: </b> ${data.marca}</p>
                  <p><b>Color: </b> ${data.color}</p>
                  <p><b>Año: </b> ${data.año}</p>
                  <p><b>Placas: </b> ${data.placas}</p>
                  </section>`;
              }
            }
            if (
              data.tipo_procedimiento_art ===
              "Lesionado por Artificio Pirotecnico"
            ) {
              detalles += `
              <h4>Informacion del Lesionado</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombre: </b> ${data.nombres}</p>
                <p><b>Apellido: </b> ${data.apellidos}</p>
                <p><b>Cedula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                </section>
                <h4>Detalles Incidente</h4>
                <section class="detalles_procedimiento">
                  <p><b>IDX: </b> ${data.idx}</p>
                  <p><b>Descripcion: </b> ${data.descripcion}</p>
                  <p><b>Status: </b> ${data.status}</p>
                </section>`;
            }
            if (
              data.tipo_procedimiento_art ===
              "Fallecido por Artificio Pirotecnico"
            ) {
              detalles += `
              <h4>Informacion del Fallecido</h4>
                <section class="detalles_procedimiento">
                <p><b>Motivo Fallcimiento: </b> ${data.motivo_fallecimiento}</p>
                <p><b>Nombre: </b> ${data.nombres}</p>
                <p><b>Apellido: </b> ${data.apellidos}</p>
                <p><b>Cedula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                </section>
                <h4>Detalles Incidente</h4>
                <section class="detalles_procedimiento">
                <p><b>Descripcion: </b> ${data.descripcion}</p>
                <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                  <p><b>Status: </b> ${data.status}</p>
                </section>`;
            }
            break;
          case "Inspeccion Establecimiento por Artificios Pirotecnicos":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                ${generateCommonDetails(data)}
                </section>
                <h4>Informacion del Comercio</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombre del Comercio: </b> ${data.nombre_comercio}</p>
                <p><b>RIF del Comercio: </b> ${data.rif_comercio}</p>
                </section>
                <h4>Informacion del Encargado</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.encargado_nombre}</p>
                <p><b>Apellidos: </b> ${data.encargado_apellidos}</p>
                <p><b>Cedula: </b> ${data.encargado_cedula}</p>
                <p><b>Sexo: </b> ${data.encargado_sexo}</p>
              </section>`;
            break;
          case "Valoración Medica":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
              ${generateCommonDetails(data)}
              </section>
              <h4>Atendido</h4>
              <section class="detalles_procedimiento">
              <p><b>Nombres: </b> ${data.nombres}</p>
              <p><b>Apellidos: </b> ${data.apellidos}</p>
              <p><b>Cedula: </b> ${data.cedula}</p>
              <p><b>Edad: </b> ${data.edad}</p>
              <p><b>Sexo: </b> ${data.sexo}</p>
              <p><b>Telefono: </b> ${data.telefono}</p>
              </section>`;
            break;
          case "Jornada Medica":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
                ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombre de la Jornada: </b> ${data.nombre_jornada}</p>
                <p><b>Cantidad Personas Atendidas: </b> ${data.cant_personas}</p>
                </section>`;
            break;
          case "Administración de Tratamiento":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(data)}
                  </section>
                  <h4>Atendido</h4>
                  <section class="detalles_procedimiento">
                  <p><b>Nombres: </b> ${data.nombres}</p>
                  <p><b>Apellidos: </b> ${data.apellidos}</p>
                  <p><b>Cédula: </b> ${data.cedula}</p>
                  <p><b>Edad: </b> ${data.edad}</p>
                  <p><b>Sexo: </b> ${data.sexo}</p>
                  <p><b>Teléfono: </b> ${data.telefono}</p>
                  </section>`;
            break;
          case "Administración de Medicamentos":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                <p><b>Teléfono: </b> ${data.telefono}</p>
                </section>`;
            break;
          case "Aerosolterapia":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                  ${generateCommonDetails(data)}
                  </section>
                  <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                <p><b>Teléfono: </b> ${data.telefono}</p>
                </section>`;
            break;
          case "Atención Local":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                <p><b>Teléfono: </b> ${data.telefono}</p>
                </section>`;
            break;
          case "Atención Prehospitalaria":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                  ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                <p><b>Teléfono: </b> ${data.telefono}</p>
                </section>`;
            break;
          case "Cuantificación de Presión Arterial":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                  ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                  <p><b>Edad: </b> ${data.edad}</p>
                  <p><b>Sexo: </b> ${data.sexo}</p>
                  <p><b>Teléfono: </b> ${data.telefono}</p>
                  </section>`;
            break;
          case "Cuantificación de Signos Vitales":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                <p><b>Teléfono: </b> ${data.telefono}</p>
                </section>`;
            break;
          case "Cura":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                  ${generateCommonDetails(data)}
                  </section>
                  <h4>Atendido</h4>
                  <section class="detalles_procedimiento">
                  <p><b>Nombres: </b> ${data.nombres}</p>
                  <p><b>Apellidos: </b> ${data.apellidos}</p>
                  <p><b>Cédula: </b> ${data.cedula}</p>
                  <p><b>Edad: </b> ${data.edad}</p>
                  <p><b>Sexo: </b> ${data.sexo}</p>
                  <p><b>Teléfono: </b> ${data.telefono}</p>
                  </section>`;
            break;
          case "Otro":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                  ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                  <p><b>Edad: </b> ${data.edad}</p>
                  <p><b>Sexo: </b> ${data.sexo}</p>
                  <p><b>Teléfono: </b> ${data.telefono}</p>
                  </section>`;
            break;
          case "Certificado de Salud Mental":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                </section>`;
            break;
          case "Consulta Bombero Activo":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                </section>`;
            break;
          case "Consulta Integrante Brigada Juvenil":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(data)}
                  </section>
                  <h4>Atendido</h4>
                  <section class="detalles_procedimiento">
                  <p><b>Nombres: </b> ${data.nombres}</p>
                  <p><b>Apellidos: </b> ${data.apellidos}</p>
                  <p><b>Cédula: </b> ${data.cedula}</p>
                  <p><b>Edad: </b> ${data.edad}</p>
                  <p><b>Sexo: </b> ${data.sexo}</p>
                  </section>`;
            break;
          case "Consulta Paciente Externo":
            detalles = `
            <h4>Detalles</h4>
                    <section class="detalles_procedimiento">
                    ${generateCommonDetails(data)}
                    </section>
                    <h4>Atendido</h4>
                    <section class="detalles_procedimiento">
                  <p><b>Nombres: </b> ${data.nombres}</p>
                  <p><b>Apellidos: </b> ${data.apellidos}</p>
                  <p><b>Cédula: </b> ${data.cedula}</p>
                  <p><b>Edad: </b> ${data.edad}</p>
                  <p><b>Sexo: </b> ${data.sexo}</p>
                </section>`;
            break;
          case "Evaluación Psicológica Postvacacional":
            detalles = `
            <h4>Detalles</h4>
              <section class="detalles_procedimiento">
              ${generateCommonDetails(data)}
              </section>
              <h4>Atendido</h4>
              <section class="detalles_procedimiento">
              <p><b>Nombres: </b> ${data.nombres}</p>
              <p><b>Apellidos: </b> ${data.apellidos}</p>
              <p><b>Cédula: </b> ${data.cedula}</p>
              <p><b>Edad: </b> ${data.edad}</p>
              <p><b>Sexo: </b> ${data.sexo}</p>
              </section>`;
            break;
          case "Evaluación Psicológica Prevacacional":
            detalles = `
            <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                ${generateCommonDetails(data)}
                </section>
                <h4>Atendido</h4>
                <section class="detalles_procedimiento">
                <p><b>Nombres: </b> ${data.nombres}</p>
                <p><b>Apellidos: </b> ${data.apellidos}</p>
                <p><b>Cédula: </b> ${data.cedula}</p>
                <p><b>Edad: </b> ${data.edad}</p>
                <p><b>Sexo: </b> ${data.sexo}</p>
                </section>`;
            break;
          case "Evaluación Personal Nuevo Ingreso":
            detalles = `
            <h4>Detalles</h4>
                  <section class="detalles_procedimiento">
                  ${generateCommonDetails(data)}
                  </section>
                  <h4>Atendido</h4>
                  <section class="detalles_procedimiento">
                  <p><b>Nombres: </b> ${data.nombres}</p>
                  <p><b>Apellidos: </b> ${data.apellidos}</p>
                  <p><b>Cédula: </b> ${data.cedula}</p>
                  <p><b>Edad: </b> ${data.edad}</p>
                  <p><b>Sexo: </b> ${data.sexo}</p>
                  </section>`;
            break;
          case "Capacitación":
            if (data.dependencia === "Capacitacion") {
              detalles = `
              <h4>Capacitacion</h4>
                      <section class="detalles_procedimiento">
                      <p><b>Tipo de Capacitacion: </b> ${data.tipo_capacitacion}</p>
                      <p><b>Clasificacion: </b> ${data.tipo_clasificacion}</p>
                      <p><b>Personas Beneficiadas: </b> ${data.personas_beneficiadas}</p>
                      </section>
                      <h4>Detalles</h4>
                      <section class="detalles_procedimiento">
                      <p><b>Descripcion: </b> ${data.descripcion}</p>
                      <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                      <p><b>Status: </b> ${data.status}</p>
                      </section>`;
            }
            if (data.dependencia === "Brigada Juvenil") {
              detalles = `
              <h4>Capacitacion</h4>
                      <section class="detalles_procedimiento">
                      <p><b>Tipo de Capacitacion: </b> ${data.tipo_capacitacion}</p>
                      <p><b>Clasificacion: </b> ${data.tipo_clasificacion}</p>
                      <p><b>Personas Beneficiadas: </b> ${data.personas_beneficiadas}</p>
                      </section>
                      <h4>Detalles</h4>
                      <section class="detalles_procedimiento">
                      <p><b>Descripcion: </b> ${data.descripcion}</p>
                      <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                      <p><b>Status: </b> ${data.status}</p>
                      </section>`;
            }
            if (data.dependencia === "Frente Preventivo") {
              detalles = `
              <h4>Capacitacion</h4>
                      <section class="detalles_procedimiento">
                      <p><b>Nombre de la Actividad: </b> ${data.nombre_actividad}</p>
                      <p><b>Estrategia: </b> ${data.estrategia}</p>
                <p><b>Personas Beneficiadas: </b> ${data.personas_beneficiadas}</p>
                </section>
                <h4>Detalles</h4>
                <section class="detalles_procedimiento">
                <p><b>Descripcion: </b> ${data.descripcion}</p>
                <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
                <p><b>Status: </b> ${data.status}</p>
                </section>`;
            }
            break;
          default:
            detalles = "<h2>Error: Tipo de Procedimiento no válido</h2>";
        }

        info_modal.innerHTML = baseInfo + detalles + "</article>";
      } catch {
        console.error("Error:", error);
      }
  });
} else {
  console.error("El contenedor #procedimientos-container no se encuentra en el DOM.");
}
});

function generateCommonDetails(
  data,
  additionalField = "",
  additionalField2 = ""
) {
  return `
      <p><b>Tipo de Procedimiento: </b> ${data.tipo_procedimiento}</p>
      ${
        additionalField
          ? `<p><b>${additionalField
              .replace(/_/g, " ")
              .replace(/\b\w/g, (c) => c.toUpperCase())}: </b> ${
              data[additionalField]
            }</p>`
          : ""
      }
      ${
        additionalField2
          ? `<p><b>${additionalField2
              .replace(/_/g, " ")
              .replace(/\b\w/g, (c) => c.toUpperCase())}: </b> ${
              data[additionalField2]
            }</p>`
          : ""
      }
      <p><b>Descripcion: </b> ${data.descripcion}</p>
      <p><b>Material Utilizado: </b> ${data.material_utilizado}</p>
      <p><b>Status: </b> ${data.status}</p>
    `;
}
