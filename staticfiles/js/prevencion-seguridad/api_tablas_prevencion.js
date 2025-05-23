const tablaPrevencionContenido = document.getElementById(
  "tabla-contenido-prevencion"
);

document.addEventListener("DOMContentLoaded", () => {
  const openModalPrevencion = document.querySelectorAll(".view-solicitudes");

  openModalPrevencion.forEach((boton) => {
    boton.addEventListener("click", async () => {
      let referencia = boton.getAttribute("data-id");

      tablaPrevencionContenido.textContent = "";

      const response = await fetchWithLoader(
        `/api/get_solicitudes/${referencia}/`
      );
      const data = await response;

      let i = 1;

      data.forEach((item) => {
        tablaPrevencionContenido.innerHTML += `
          <tr>
              <td>${i}</td>
              <td>Solicitud</td>
              <td>${item.tipo_solicitud}</td>
              <td>${item.solicitante}</td>
              <td>${item.fecha}</td>
              <td>
              <button class="btn btn-danger" id="Modificar_documento" data-solicitud=${item.id_solicitud}><svg width="30px" height="30px" viewBox="0 0 24 24" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                        <g id="SVGRepo_iconCarrier">
                          <path
                            d="M20.1497 7.93997L8.27971 19.81C7.21971 20.88 4.04971 21.3699 3.27971 20.6599C2.50971 19.9499 3.06969 16.78 4.12969 15.71L15.9997 3.84C16.5478 3.31801 17.2783 3.03097 18.0351 3.04019C18.7919 3.04942 19.5151 3.35418 20.0503 3.88938C20.5855 4.42457 20.8903 5.14781 20.8995 5.90463C20.9088 6.66146 20.6217 7.39189 20.0997 7.93997H20.1497Z"
                            stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
                          <path d="M21 21H12" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"
                            stroke-linejoin="round"></path>
                        </g>
                      </svg></button>
                  <button class="btn btn-danger" id="Eliminar_documento" data-solicitud="${item.id_solicitud}" ><svg width="30px" height="30px" viewBox="0 0 24 24" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                        <g id="SVGRepo_iconCarrier">
                          <path d="M4 7H20" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
                            stroke-linejoin="round"></path>
                          <path
                            d="M6 10L7.70141 19.3578C7.87432 20.3088 8.70258 21 9.66915 21H14.3308C15.2974 21 16.1257 20.3087 16.2986 19.3578L18 10"
                            stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                          <path d="M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5V7H9V5Z" stroke="#ffffff"
                            stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                        </g>
                      </svg></button>
                  <button class="btn btn-danger" id="Ver_documento" data-solicitud="${item.id_solicitud}" data-tipo-documento="Solicitud"><svg width="30px" height="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M10.9436 1.25H13.0564C14.8942 1.24998 16.3498 1.24997 17.489 1.40314C18.6614 1.56076 19.6104 1.89288 20.3588 2.64124C21.1071 3.38961 21.4392 4.33856 21.5969 5.51098C21.75 6.65019 21.75 8.10583 21.75 9.94359V14.0564C21.75 15.8942 21.75 17.3498 21.5969 18.489C21.4392 19.6614 21.1071 20.6104 20.3588 21.3588C19.6104 22.1071 18.6614 22.4392 17.489 22.5969C16.3498 22.75 14.8942 22.75 13.0564 22.75H10.9436C9.10583 22.75 7.65019 22.75 6.51098 22.5969C5.33856 22.4392 4.38961 22.1071 3.64124 21.3588C2.89288 20.6104 2.56076 19.6614 2.40314 18.489C2.24997 17.3498 2.24998 15.8942 2.25 14.0564V9.94358C2.24998 8.10582 2.24997 6.65019 2.40314 5.51098C2.56076 4.33856 2.89288 3.38961 3.64124 2.64124C4.38961 1.89288 5.33856 1.56076 6.51098 1.40314C7.65019 1.24997 9.10582 1.24998 10.9436 1.25ZM6.71085 2.88976C5.70476 3.02502 5.12511 3.27869 4.7019 3.7019C4.27869 4.12511 4.02502 4.70476 3.88976 5.71085C3.75159 6.73851 3.75 8.09318 3.75 10V14C3.75 15.9068 3.75159 17.2615 3.88976 18.2892C4.02502 19.2952 4.27869 19.8749 4.7019 20.2981C5.12511 20.7213 5.70476 20.975 6.71085 21.1102C7.73851 21.2484 9.09318 21.25 11 21.25H13C14.9068 21.25 16.2615 21.2484 17.2892 21.1102C18.2952 20.975 18.8749 20.7213 19.2981 20.2981C19.7213 19.8749 19.975 19.2952 20.1102 18.2892C20.2484 17.2615 20.25 15.9068 20.25 14V10C20.25 8.09318 20.2484 6.73851 20.1102 5.71085C19.975 4.70476 19.7213 4.12511 19.2981 3.7019C18.8749 3.27869 18.2952 3.02502 17.2892 2.88976C16.2615 2.75159 14.9068 2.75 13 2.75H11C9.09318 2.75 7.73851 2.75159 6.71085 2.88976ZM7.25 8C7.25 7.58579 7.58579 7.25 8 7.25H16C16.4142 7.25 16.75 7.58579 16.75 8C16.75 8.41421 16.4142 8.75 16 8.75H8C7.58579 8.75 7.25 8.41421 7.25 8ZM7.25 12C7.25 11.5858 7.58579 11.25 8 11.25H16C16.4142 11.25 16.75 11.5858 16.75 12C16.75 12.4142 16.4142 12.75 16 12.75H8C7.58579 12.75 7.25 12.4142 7.25 12ZM7.25 16C7.25 15.5858 7.58579 15.25 8 15.25H13C13.4142 15.25 13.75 15.5858 13.75 16C13.75 16.4142 13.4142 16.75 13 16.75H8C7.58579 16.75 7.25 16.4142 7.25 16Z" fill="#ffffff"></path> </g></svg></button>
              </td>
          <tr>
          `;

        let tieneDocumentosFaltantes =
          Array.isArray(item.documentos_faltantes) &&
          item.documentos_faltantes.length > 0 &&
          item.documentos_faltantes[0] !==
            "Todos los documentos están en orden";

        let tieneDocumentosProximosVencer =
          Array.isArray(item.documentos_proximos_vencer) &&
          item.documentos_proximos_vencer.length > 0 &&
          item.documentos_proximos_vencer[0] !==
            "No hay documentos próximos a vencer";

        let tieneDocumentosVencidos =
          Array.isArray(item.documentos_vencidos) &&
          item.documentos_vencidos.length > 0 &&
          item.documentos_vencidos[0] !== "No hay documentos vencidos";

        if (tieneDocumentosFaltantes) {
          let documentosHTML = item.documentos_faltantes.join(", ");
          tablaPrevencionContenido.innerHTML += `
              <tr>
                  <td colspan="6" style="color: red; font-weight: bold; text-align: justify;">
                      ⚠️ Documentos Faltantes: ${documentosHTML}
                  </td>
              </tr>
          `;
        }

        if (tieneDocumentosProximosVencer) {
          let proximosVencerHTML = item.documentos_proximos_vencer.join(", ");
          tablaPrevencionContenido.innerHTML += `
              <tr>
                  <td colspan="6" style="color: orange; font-weight: bold; text-align: justify;">
                      ⏳ Documentos Próximos a Vencer: ${proximosVencerHTML}
                  </td>
              </tr>
          `;
        }

        if (tieneDocumentosVencidos) {
          let vencidosHTML = item.documentos_vencidos.join(", ");
          tablaPrevencionContenido.innerHTML += `
              <tr>
                  <td colspan="6" style="color: darkred; font-weight: bold; text-align: justify;">
                      ❌ Documentos Vencidos: ${vencidosHTML}
                  </td>
              </tr>
          `;
        }

        // Solo mostrar "Todos los documentos están en orden" si no hay documentos pendientes, vencidos o próximos a vencer
        if (
          !tieneDocumentosFaltantes &&
          !tieneDocumentosProximosVencer &&
          !tieneDocumentosVencidos
        ) {
          tablaPrevencionContenido.innerHTML += `
          <tr>
              <td colspan="6" style="color: green; font-weight: bold; text-align: justify;">
                  ✅ Todos los documentos están en orden
              </td>
          </tr>
      `;
        }

        i++;

        tablaPrevencionContenido.innerHTML += `
          <tr>
            <td>${i}</td>
            <td>Guia de Inspeccion</td>
            <td>${item.tipo_solicitud}</td>
            <td>${item.solicitante}</td>
            <td>${item.fecha}</td>
            <td>
                  <button class="btn btn-danger" id="Ver_documento" data-solicitud="${item.id_solicitud}" data-tipo-documento="Guia"><svg width="30px" height="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M10.9436 1.25H13.0564C14.8942 1.24998 16.3498 1.24997 17.489 1.40314C18.6614 1.56076 19.6104 1.89288 20.3588 2.64124C21.1071 3.38961 21.4392 4.33856 21.5969 5.51098C21.75 6.65019 21.75 8.10583 21.75 9.94359V14.0564C21.75 15.8942 21.75 17.3498 21.5969 18.489C21.4392 19.6614 21.1071 20.6104 20.3588 21.3588C19.6104 22.1071 18.6614 22.4392 17.489 22.5969C16.3498 22.75 14.8942 22.75 13.0564 22.75H10.9436C9.10583 22.75 7.65019 22.75 6.51098 22.5969C5.33856 22.4392 4.38961 22.1071 3.64124 21.3588C2.89288 20.6104 2.56076 19.6614 2.40314 18.489C2.24997 17.3498 2.24998 15.8942 2.25 14.0564V9.94358C2.24998 8.10582 2.24997 6.65019 2.40314 5.51098C2.56076 4.33856 2.89288 3.38961 3.64124 2.64124C4.38961 1.89288 5.33856 1.56076 6.51098 1.40314C7.65019 1.24997 9.10582 1.24998 10.9436 1.25ZM6.71085 2.88976C5.70476 3.02502 5.12511 3.27869 4.7019 3.7019C4.27869 4.12511 4.02502 4.70476 3.88976 5.71085C3.75159 6.73851 3.75 8.09318 3.75 10V14C3.75 15.9068 3.75159 17.2615 3.88976 18.2892C4.02502 19.2952 4.27869 19.8749 4.7019 20.2981C5.12511 20.7213 5.70476 20.975 6.71085 21.1102C7.73851 21.2484 9.09318 21.25 11 21.25H13C14.9068 21.25 16.2615 21.2484 17.2892 21.1102C18.2952 20.975 18.8749 20.7213 19.2981 20.2981C19.7213 19.8749 19.975 19.2952 20.1102 18.2892C20.2484 17.2615 20.25 15.9068 20.25 14V10C20.25 8.09318 20.2484 6.73851 20.1102 5.71085C19.975 4.70476 19.7213 4.12511 19.2981 3.7019C18.8749 3.27869 18.2952 3.02502 17.2892 2.88976C16.2615 2.75159 14.9068 2.75 13 2.75H11C9.09318 2.75 7.73851 2.75159 6.71085 2.88976ZM7.25 8C7.25 7.58579 7.58579 7.25 8 7.25H16C16.4142 7.25 16.75 7.58579 16.75 8C16.75 8.41421 16.4142 8.75 16 8.75H8C7.58579 8.75 7.25 8.41421 7.25 8ZM7.25 12C7.25 11.5858 7.58579 11.25 8 11.25H16C16.4142 11.25 16.75 11.5858 16.75 12C16.75 12.4142 16.4142 12.75 16 12.75H8C7.58579 12.75 7.25 12.4142 7.25 12ZM7.25 16C7.25 15.5858 7.58579 15.25 8 15.25H13C13.4142 15.25 13.75 15.5858 13.75 16C13.75 16.4142 13.4142 16.75 13 16.75H8C7.58579 16.75 7.25 16.4142 7.25 16Z" fill="#ffffff"></path> </g></svg></button>
              </td>
          <tr>
          `;

        tieneDocumentosFaltantes =
          Array.isArray(item.documentos_faltantes) &&
          item.documentos_faltantes.length > 0 &&
          item.documentos_faltantes[0] !==
            "Todos los documentos están en orden";

        tieneDocumentosProximosVencer =
          Array.isArray(item.documentos_proximos_vencer) &&
          item.documentos_proximos_vencer.length > 0 &&
          item.documentos_proximos_vencer[0] !==
            "No hay documentos próximos a vencer";

        tieneDocumentosVencidos =
          Array.isArray(item.documentos_vencidos) &&
          item.documentos_vencidos.length > 0 &&
          item.documentos_vencidos[0] !== "No hay documentos vencidos";

        if (tieneDocumentosFaltantes) {
          let documentosHTML = item.documentos_faltantes.join(", ");
          tablaPrevencionContenido.innerHTML += `
            <tr>
                <td colspan="6" style="color: red; font-weight: bold; text-align: justify;">
                    ⚠️ Documentos Faltantes: ${documentosHTML}
                </td>
            </tr>
        `;
        }

        if (tieneDocumentosProximosVencer) {
          let proximosVencerHTML = item.documentos_proximos_vencer.join(", ");
          tablaPrevencionContenido.innerHTML += `
            <tr>
                <td colspan="6" style="color: orange; font-weight: bold; text-align: justify;">
                    ⏳ Documentos Próximos a Vencer: ${proximosVencerHTML}
                </td>
            </tr>
        `;
        }

        if (tieneDocumentosVencidos) {
          let vencidosHTML = item.documentos_vencidos.join(", ");
          tablaPrevencionContenido.innerHTML += `
            <tr>
                <td colspan="6" style="color: darkred; font-weight: bold; text-align: justify;">
                    ❌ Documentos Vencidos: ${vencidosHTML}
                </td>
            </tr>
        `;
        }

        // Solo mostrar "Todos los documentos están en orden" si no hay documentos pendientes, vencidos o próximos a vencer
        if (
          !tieneDocumentosFaltantes &&
          !tieneDocumentosProximosVencer &&
          !tieneDocumentosVencidos
        ) {
          tablaPrevencionContenido.innerHTML += `
          <tr>
              <td colspan="6" style="color: green; font-weight: bold; text-align: justify;">
                  ✅ Todos los documentos están en orden
              </td>
          </tr>
      `;
        }

        i++;
      });

      descargarWordSolicitud();
      eliminarSolicitud();
      editarSolicitud();
    });
  });
});
