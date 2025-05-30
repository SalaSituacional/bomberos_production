async function remplazarVariablesPDF() {
    try {
        // 1. Obtener valores de los campos HTML
        const variables = {
            hechos: document.getElementById('hechosvialestotal').textContent.replace(/[()]/g, '') || '0',
            consultas: document.getElementById('consultasmedicastotales').textContent.replace(/[()]/g, '') || '0',
            operaciones: document.getElementById('operacionescomunicacionespuestosdeavanzadatotales').textContent.replace(/[()]/g, '') || '0',
            abordajescomunidades: document.getElementById('abordajescomunidadestrasladosambulancia').textContent.replace(/[()]/g, '') || '0',
            atencionesprehospitalarias: document.getElementById('atencionesprehospitalariasverificaciondesignostotales').textContent.replace(/[()]/g, '') || '0',
            serviciosespeciales: document.getElementById('serviciosespecialestotales').textContent.replace(/[()]/g, '') || '0',
            inspeccionesestablecimientos: document.getElementById('insepccionesestablecimientoscomercialestotales').textContent.replace(/[()]/g, '') || '0',
            inspeccionesriesgos: document.getElementById('inspeccionesazonasderiesgototales').textContent.replace(/[()]/g, '') || '0',
            incendios: document.getElementById('incendiosestructuralesglpvegetaciontotales').textContent.replace(/[()]/g, '') || '0',
            rescates: document.getElementById('rescatestotales').textContent.replace(/[()]/g, '') || '0',
            himenopteros: document.getElementById('heminopterostotales').textContent.replace(/[()]/g, '') || '0',
            talaspodas: document.getElementById('talaspodastotales').textContent.replace(/[()]/g, '') || '0',
            totales: document.getElementById('resultadostotales').textContent.replace(/[()]/g, '') || '0',
            // Agrega más variables según necesites
        };

        // 2. Cargar el PDF base
        const pdfUrl = planilla_pdf;
        const existingPdfBytes = await fetch(pdfUrl).then(res => res.arrayBuffer());

        // 3. Cargar el PDF con pdf-lib
        const pdfDoc = await PDFLib.PDFDocument.load(existingPdfBytes);
        const pages = pdfDoc.getPages();
        const firstPage = pages[0];

        // 4. Configuración de texto
        const fontSize = 13;
        const font = await pdfDoc.embedFont(PDFLib.StandardFonts.Helvetica);
        const textColor = PDFLib.rgb(0, 0, 0);

        // 5. Definir manualmente las posiciones de las variables
        // (Debes ajustar estas coordenadas según tu PDF específico)
        const variablePositions = {
            totales: { x: 603, y: 417, page: 0 }, // Ejemplo - ajusta estas coordenadas
            hechos: { x: 603, y: 400, page: 0 }, // Ejemplo - ajusta estas coordenadas
            consultas: { x: 603, y: 383, page: 0 }, // Ejemplo - ajusta estas coordenadas
            operaciones: { x: 603, y: 358, page: 0 }, // Ejemplo - ajusta estas coordenadas
            abordajescomunidades: { x: 603, y: 325, page: 0 }, // Ejemplo - ajusta estas coordenadas
            atencionesprehospitalarias: { x: 603, y: 290, page: 0 }, // Ejemplo - ajusta estas coordenadas
            serviciosespeciales: { x: 603, y: 268, page: 0 }, // Ejemplo - ajusta estas coordenadas
            inspeccionesestablecimientos: { x: 603, y: 249, page: 0 }, // Ejemplo - ajusta estas coordenadas
            inspeccionesriesgos: { x: 603, y: 232, page: 0 }, // Ejemplo - ajusta estas coordenadas
            incendios: { x: 603, y: 210, page: 0 }, // Ejemplo - ajusta estas coordenadas
            rescates: { x: 603, y: 190, page: 0 }, // Ejemplo - ajusta estas coordenadas
            himenopteros: { x: 603, y: 172, page: 0 }, // Ejemplo - ajusta estas coordenadas
            talaspodas: { x: 603, y: 155, page: 0 }, // Ejemplo - ajusta estas coordenadas
            // Agrega más posiciones para otras variables
        };

        // 6. Reemplazar cada variable
        for (const [variableName, position] of Object.entries(variablePositions)) {
            if (variables[variableName] !== undefined) {
                pages[position.page].drawText(variables[variableName].toString(), {
                    x: position.x,
                    y: position.y,
                    size: fontSize,
                    font,
                    color: textColor
                });
            }
        }

        // 7. Guardar el PDF modificado
        const pdfBytes = await pdfDoc.save();
        download(pdfBytes, "documento_actualizado.pdf", "application/pdf");

    } catch (error) {
        console.error('Error al procesar el PDF:', error);
        alert('Error al generar PDF: ' + error.message);
    }
}