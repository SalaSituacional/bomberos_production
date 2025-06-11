document.addEventListener("DOMContentLoaded", () => {
  // Configuración inicial
  const modal = new bootstrap.Modal(document.getElementById("modal-info"));
  const tablaContenido = document.getElementById("tabla-contenido-prevencion");
  const loadingScreen = document.getElementById("loadingScreen");
  let activeRequests = 0;

  // Configuración de documentos por dependencia
  const DocumentConfig = {
    types: {
      Solicitud: {
        endpoint: '/seguridad_prevencion/generar_documento_guia/',
        filenamePrefix: 'Solicitud_'
      },
      Guia: {
        endpoint: '/seguridad_prevencion/generar_documento_inspeccion/',
        filenamePrefix: 'Guia_'
      },
      Eliminar: {
        endpoint: '/seguridad_prevencion/api/eliminar_solicitudes/'
      }
    },
    // Plantillas por dependencia
    templates: {
      'San Cristobal': {
        solicitud: 'Solictud_2025.pdf',
        inspeccion: 'Inspeccion_2025.pdf'
      },
      'Junin': {
        solicitud: 'Solicitud_2025 (junin).pdf',
        inspeccion: 'Inspeccion_2025 (junin).pdf'
      },
      'default': {
        solicitud: 'Solictud.pdf',
        inspeccion: 'Inspeccion.pdf'
      }
    }
  };

  // Función para crear fila de documento
  const crearFilaDocumento = (item, tipo, index) => {
    const tieneProblemas = 
      item.documentos_faltantes[0] !== "Todos los documentos están en orden" ||
      item.documentos_proximos_vencer[0] !== "No hay documentos próximos a vencer" ||
      item.documentos_vencidos[0] !== "No hay documentos vencidos";

    return `
      <tr>
        <td>${index}</td>
        <td>${tipo}</td>
        <td>${item.tipo_solicitud}</td>
        <td>${item.solicitante}</td>
        <td>${item.fecha}</td>
        <td class="text-nowrap">
          ${item.tiene_requisitos ? `
            <a href="/seguridad_prevencion/editar_solicitud/${item.id_solicitud}" class="btn btn-sm btn-primary" title="Editar">
              <i class="bi bi-pencil"></i>
            </a>
            ` : ''}
          <button class="btn btn-danger btn-sm mx-1 eliminar-documento" data-solicitud="${item.id_solicitud}" title="Eliminar">
            <i class="bi bi-trash"></i>
          </button>
          <button class="btn btn-success btn-sm mx-1 descargar-guia" 
                  data-solicitud="${item.id_solicitud}" 
                  data-departamento="${item.comercio_departamento || 'default'}"
                  title="Descargar Guía de Inspección">
            <i class="bi bi-download"></i>
          </button>
          <button class="btn btn-danger btn-sm mx-1 ver-documento" 
                  data-solicitud="${item.id_solicitud}" 
                  data-tipo-documento="Solicitud"
                  data-departamento="${item.comercio_departamento || 'default'}"
                  title="Descargar Solicitud">
            <i class="bi bi-file-text"></i>
          </button>
        </td>
      </tr>
      ${tieneProblemas ? `
        <tr class="table-${tipo === 'Solicitud' ? 'warning' : 'info'}">
          <td colspan="6" class="small">
            ${item.documentos_faltantes[0] !== "Todos los documentos están en orden" ? 
              `<div class="text-danger mb-1"><i class="bi bi-exclamation-circle"></i> <strong>Faltantes:</strong> ${item.documentos_faltantes.join(', ')}</div>` : ''}
            ${item.documentos_proximos_vencer[0] !== "No hay documentos próximos a vencer" ? 
              `<div class="text-warning mb-1"><i class="bi bi-clock"></i> <strong>Próximos a vencer:</strong> ${item.documentos_proximos_vencer.join(', ')}</div>` : ''}
            ${item.documentos_vencidos[0] !== "No hay documentos vencidos" ? 
              `<div class="text-danger"><i class="bi bi-x-circle"></i> <strong>Vencidos:</strong> ${item.documentos_vencidos.join(', ')}</div>` : ''}
          </td>
        </tr>
      ` : `
        <tr class="table-success">
          <td colspan="6" class="small text-center">
            <i class="bi bi-check-circle"></i> Todos los documentos están en orden
          </td>
        </tr>
      `}
    `;
  };

  // Control de pantalla de carga
  const showLoading = () => {
    activeRequests++;
    loadingScreen.style.display = 'flex';
  };

  const hideLoading = () => {
    if (activeRequests > 0) activeRequests--;
    if (activeRequests === 0) loadingScreen.style.display = 'none';
  };

  // Función para fetch con manejo de errores
  const fetchWithLoading = async (url, options = {}) => {
    showLoading();
    try {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } finally {
      hideLoading();
    }
  };

  // Manejador para ver solicitudes
  const handleViewSolicitudes = async (boton) => {
    const referencia = boton.dataset.id;
    
    try {
      tablaContenido.innerHTML = '';
      modal.show();
      
      const data = await fetchWithLoading(`/seguridad_prevencion/api/get_solicitudes/${referencia}/`);
      
      if (data.length === 0) {
        tablaContenido.innerHTML = `
          <tr>
            <td colspan="6" class="text-center py-4 text-muted">
              No se encontraron solicitudes para este comercio
            </td>
          </tr>
        `;
        return;
      }
      
      data.forEach((item, index) => {
        tablaContenido.innerHTML += crearFilaDocumento(item, "Solicitud", index * 2 + 1);
      });
      
    } catch (error) {
      console.error("Error:", error);
      tablaContenido.innerHTML = `
        <tr>
          <td colspan="6" class="text-center py-4 text-danger">
            <i class="bi bi-exclamation-triangle"></i> Error al cargar los datos
          </td>
        </tr>
      `;
    }
  };

  // Manejador para descargar guía
  const handleDownloadGuia = (boton) => {
    const solicitudId = boton.dataset.solicitud;
    const dependencia = boton.dataset.departamento;
    const url = `/seguridad_prevencion/generar_documento_inspeccion/${solicitudId}/?dependencia=${dependencia}`;
    window.open(url, '_blank');
  };

  // Manejador para ver documento
  const handleViewDocument = async (boton) => {
    const solicitudId = boton.dataset.solicitud;
    const dependencia = boton.dataset.departamento;
    const url = `/seguridad_prevencion/generar_documento_guia/${solicitudId}/?dependencia=${dependencia}`;
    window.open(url, '_blank');
  };

  // Manejador de eventos delegado
  document.addEventListener('click', (e) => {
    if (e.target.closest('.view-solicitudes')) {
      handleViewSolicitudes(e.target.closest('.view-solicitudes'));
    }
    else if (e.target.closest('.descargar-guia')) {
      handleDownloadGuia(e.target.closest('.descargar-guia'));
    }
    else if (e.target.closest('.ver-documento')) {
      handleViewDocument(e.target.closest('.ver-documento'));
    }
    else if (e.target.closest('.eliminar-documento')) {
      handleDeleteDocument(e.target.closest('.eliminar-documento'));
    }
  });
});