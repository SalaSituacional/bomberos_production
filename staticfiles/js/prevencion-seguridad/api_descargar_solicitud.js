// const DocumentConfig = {
//   types: {
//     Solicitud: {
//       endpoint: '/seguridad_prevencion/generar_documento_guia/',
//       filenamePrefix: 'Solicitud_'
//     },
//     Guia: {
//       endpoint: '/seguridad_prevencion/generar_documento_inspeccion/',
//       filenamePrefix: 'Guia_'
//     }
//   }
// };

// // Estado global para control de peticiones
// const AppState = {
//   activeRequests: 0,
//   loadingScreen: null
// };

// // Función principal que se ejecuta al cargar la página
// document.addEventListener('DOMContentLoaded', () => {
//   // Inicializar pantalla de carga
//   AppState.loadingScreen = document.getElementById('loadingScreen');
  
//   // Configurar manejadores
//   setupModalOpeners();
//   setupModalContentHandlers();
// });

// // Configura los botones que abren la modal
// function setupModalOpeners() {
//   document.addEventListener('click', (e) => {
//     if (e.target.closest('.view-solicitudes')) {
//       setTimeout(setupModalContentHandlers, 100);
//     }
//   });
// }

// // Configura los manejadores para los botones dentro de la modal
// function setupModalContentHandlers() {
//   const modalContent = document.getElementById('modal-info');
  
//   if (!modalContent) return;

//   modalContent.addEventListener('click', async (e) => {
//     const viewBtn = e.target.closest('#Ver_documento');
//     if (!viewBtn) return;

//     e.preventDefault();
//     await processDocumentGeneration(viewBtn);
//   });
// }

// // Maneja la generación del documento
// async function processDocumentGeneration(button) {
//   const referencia = button.dataset.solicitud;
//   const tipo = button.dataset.tipoDocumento;
//   const config = DocumentConfig.types[tipo];

//   if (!config) {
//     console.error('Tipo de documento no configurado:', tipo);
//     return;
//   }

//   try {
//     showLoadingScreen();
    
//     const url = `${config.endpoint}${referencia}/`;
//     const nombreArchivo = `${config.filenamePrefix}${referencia}.pdf`;
    
//     const response = await fetchWithLoading(url);
//     if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
    
//     const blob = await response.blob();
//     openPdfInNewTab(blob, nombreArchivo);
//   } catch (error) {
//     console.error('Error al generar documento:', error);
//     showError('Error al generar el documento. Por favor intente nuevamente.');
//   } finally {
//     hideLoadingScreen();
//   }
// }

// // Función para fetch con control de pantalla de carga
// async function fetchWithLoading(url, options = {}) {
//   try {
//     showLoadingScreen();
//     const response = await fetch(url, options);
//     return response;
//   } catch (error) {
//     throw error;
//   } finally {
//     hideLoadingScreen();
//   }
// }

// // Función para abrir PDF en nueva pestaña
// function openPdfInNewTab(blob, filename) {
//   const pdfUrl = URL.createObjectURL(blob);
//   const newWindow = window.open(pdfUrl, '_blank');
  
//   if (newWindow) {
//     newWindow.document.title = filename;
//     newWindow.focus();
//   }
// }

// // Control de la pantalla de carga
// function showLoadingScreen() {
//   AppState.activeRequests++;
//   updateLoadingScreen();
// }

// function hideLoadingScreen() {
//   if (AppState.activeRequests > 0) {
//     AppState.activeRequests--;
//   }
//   updateLoadingScreen();
// }

// function updateLoadingScreen() {
//   if (!AppState.loadingScreen) return;
  
//   if (AppState.activeRequests > 0) {
//     AppState.loadingScreen.style.display = 'flex';
//   } else {
//     AppState.loadingScreen.style.display = 'none';
//   }
// }

// // Mostrar errores
// function showError(message) {
//   const errorToast = document.createElement('div');
//   errorToast.className = 'alert alert-danger position-fixed top-0 end-0 m-3';
//   errorToast.style.zIndex = '9999';
//   errorToast.textContent = message;
//   document.body.appendChild(errorToast);
  
//   setTimeout(() => {
//     errorToast.remove();
//   }, 5000);
// }