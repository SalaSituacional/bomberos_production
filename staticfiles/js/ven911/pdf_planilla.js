// async function remplazarVariablesPDF() {
//     try {
//         // 1. Obtener valores de los campos HTML
//         const variables = {
//             hechos: document.getElementById('hechosvialestotal').textContent.replace(/[()]/g, '') || '00',
//             consultas: document.getElementById('consultasmedicastotales').textContent.replace(/[()]/g, '') || '00',
//             operaciones: document.getElementById('operacionescomunicacionespuestosdeavanzadatotales').textContent.replace(/[()]/g, '') || '00',
//             abordajescomunidades: document.getElementById('abordajescomunidadestrasladosambulancia').textContent.replace(/[()]/g, '') || '00',
//             atencionesprehospitalarias: document.getElementById('atencionesprehospitalariasverificaciondesignostotales').textContent.replace(/[()]/g, '') || '00',
//             serviciosespeciales: document.getElementById('serviciosespecialestotales').textContent.replace(/[()]/g, '') || '00',
//             inspeccionesestablecimientos: document.getElementById('insepccionesestablecimientoscomercialestotales').textContent.replace(/[()]/g, '') || '00',
//             inspeccionesriesgos: document.getElementById('inspeccionesazonasderiesgototales').textContent.replace(/[()]/g, '') || '00',
//             incendios: document.getElementById('incendiosestructuralesglpvegetaciontotales').textContent.replace(/[()]/g, '') || '00',
//             rescates: document.getElementById('rescatestotales').textContent.replace(/[()]/g, '') || '00',
//             povapostamientos: document.getElementById('pov-apostamientostotales').textContent.replace(/[()]/g, '') || '00',
//             talaspodas: document.getElementById('talaspodastotales').textContent.replace(/[()]/g, '') || '00',
//             totales: document.getElementById('resultadostotales').textContent.replace(/[()]/g, '') || '00',
//             // Agrega más variables según necesites
//         };

//         // 2. Cargar el PDF base
//         const pdfUrl = planilla_pdf;
//         const existingPdfBytes = await fetch(pdfUrl).then(res => res.arrayBuffer());

//         // 3. Cargar el PDF con pdf-lib
//         const pdfDoc = await PDFLib.PDFDocument.load(existingPdfBytes);
//         const pages = pdfDoc.getPages();
//         const firstPage = pages[0];

//         // 4. Configuración de texto
//         const fontSize = 13;
//         // Carga la fuente Helvetica-Bold para el texto en negrita
//         const font = await pdfDoc.embedFont(PDFLib.StandardFonts.Helvetica);
//         const boldFont = await pdfDoc.embedFont(PDFLib.StandardFonts.HelveticaBold); // Carga la fuente negrita
//         const textColor = PDFLib.rgb(0, 0, 0);

//         // 5. Definir manualmente las posiciones de las variables
//         // (Debes ajustar estas coordenadas según tu PDF específico)
//         const variablePositions = {
//             totales: { x: 680, y: 372, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             hechos: { x: 680, y: 353, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             consultas: { x: 680, y: 335, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             operaciones: { x: 680, y: 318, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             abordajescomunidades: { x: 680, y: 300, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             atencionesprehospitalarias: { x: 680, y: 284, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             serviciosespeciales: { x: 680, y: 266, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             incendios: { x: 680, y: 242, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             talaspodas: { x: 680, y: 216, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             povapostamientos: { x: 680, y: 200, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             rescates: { x: 680, y: 183, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             inspeccionesestablecimientos: { x: 680, y: 165, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             inspeccionesriesgos: { x: 680, y: 148, page: 0 }, // Ejemplo - ajusta estas coordenadas
//             // Agrega más posiciones para otras variables
//         };

//         // 6. Reemplazar cada variable
//         for (const [variableName, position] of Object.entries(variablePositions)) {
//             if (variables[variableName] !== undefined) {
//                 // Usa la fuente 'boldFont' para los números
//                 pages[position.page].drawText(variables[variableName].toString(), {
//                     x: position.x,
//                     y: position.y,
//                     size: fontSize,
//                     font: boldFont, // Aquí cambiamos a la fuente negrita
//                     color: textColor
//                 });
//             }
//         }

//         // 7. Guardar el PDF modificado
//         const pdfBytes = await pdfDoc.save();
//         download(pdfBytes, "ReporteDiariasAlcalde.pdf", "application/pdf");

//     } catch (error) {
//         console.error('Error al procesar el PDF:', error);
//         alert('Error al generar PDF: ' + error.message);
//     }
// }

async function remplazarVariablesPDF() {
    try {
        // Función auxiliar para formatear los números a doble dígito
        const formatNumber = (num) => {
            const parsedNum = parseInt(num, 10);
            if (isNaN(parsedNum)) {
                return '00'; // Retorna '00' si no es un número válido
            }
            return parsedNum < 10 ? `0${parsedNum}` : parsedNum.toString();
        };

        // 1. Obtener valores de los campos HTML y aplicar el formato
        const variables = {
            hechos: formatNumber(document.getElementById('hechosvialestotal').textContent.replace(/[()]/g, '')),
            consultas: formatNumber(document.getElementById('consultasmedicastotales').textContent.replace(/[()]/g, '')),
            operaciones: formatNumber(document.getElementById('operacionescomunicacionespuestosdeavanzadatotales').textContent.replace(/[()]/g, '')),
            abordajescomunidades: formatNumber(document.getElementById('abordajescomunidadestrasladosambulancia').textContent.replace(/[()]/g, '')),
            atencionesprehospitalarias: formatNumber(document.getElementById('atencionesprehospitalariasverificaciondesignostotales').textContent.replace(/[()]/g, '')),
            serviciosespeciales: formatNumber(document.getElementById('serviciosespecialestotales').textContent.replace(/[()]/g, '')),
            inspeccionesestablecimientos: formatNumber(document.getElementById('insepccionesestablecimientoscomercialestotales').textContent.replace(/[()]/g, '')),
            inspeccionesriesgos: formatNumber(document.getElementById('inspeccionesazonasderiesgototales').textContent.replace(/[()]/g, '')),
            incendios: formatNumber(document.getElementById('incendiosestructuralesglpvegetaciontotales').textContent.replace(/[()]/g, '')),
            rescates: formatNumber(document.getElementById('rescatestotales').textContent.replace(/[()]/g, '')),
            povapostamientos: formatNumber(document.getElementById('pov-apostamientostotales').textContent.replace(/[()]/g, '')),
            talaspodas: formatNumber(document.getElementById('talaspodastotales').textContent.replace(/[()]/g, '')),
            totales: formatNumber(document.getElementById('resultadostotales').textContent.replace(/[()]/g, '')),
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
        const boldFont = await pdfDoc.embedFont(PDFLib.StandardFonts.HelveticaBold); // Carga la fuente negrita
        const textColor = PDFLib.rgb(0, 0, 0);

        // 5. Definir manualmente las posiciones de las variables
        // (Debes ajustar estas coordenadas según tu PDF específico)
        const variablePositions = {
            totales: { x: 675, y: 372, page: 0 },
            hechos: { x: 675, y: 353, page: 0 },
            consultas: { x: 675, y: 335, page: 0 },
            operaciones: { x: 675, y: 318, page: 0 },
            abordajescomunidades: { x: 675, y: 300, page: 0 },
            atencionesprehospitalarias: { x: 675, y: 284, page: 0 },
            serviciosespeciales: { x: 675, y: 266, page: 0 },
            incendios: { x: 675, y: 242, page: 0 },
            talaspodas: { x: 675, y: 216, page: 0 },
            povapostamientos: { x: 675, y: 200, page: 0 },
            rescates: { x: 675, y: 183, page: 0 },
            inspeccionesestablecimientos: { x: 675, y: 165, page: 0 },
            inspeccionesriesgos: { x: 675, y: 148, page: 0 },
            // Agrega más posiciones para otras variables
        };

        // 6. Reemplazar cada variable
        for (const [variableName, position] of Object.entries(variablePositions)) {
            if (variables[variableName] !== undefined) {
                pages[position.page].drawText(variables[variableName].toString(), {
                    x: position.x,
                    y: position.y,
                    size: fontSize,
                    font: boldFont,
                    color: textColor
                });
            }
        }

        // 7. Guardar el PDF modificado
        const pdfBytes = await pdfDoc.save();
        download(pdfBytes, "ReporteDiariasAlcalde.pdf", "application/pdf");

    } catch (error) {
        console.error('Error al procesar el PDF:', error);
        alert('Error al generar PDF: ' + error.message);
    }
}