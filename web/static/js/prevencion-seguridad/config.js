// app-config.js
window.AppConfig = {
  endpoints: {
    solicitud: '/seguridad_prevencion/generar_documento_guia/',
    guia: '/seguridad_prevencion/generar_documento_inspeccion/',
    eliminar: '/seguridad_prevencion/api/eliminar_solicitudes/'
  },
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