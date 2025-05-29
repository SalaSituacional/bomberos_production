// Al cargar la página, dejamos el input vacío inicialmente
document.addEventListener('DOMContentLoaded', function () {
    obtenerServicios(); // Cargará todos los registros
});
// Función para obtener los servicios y actualizar el DOM
async function obtenerServicios() {
    try {
        const fechaInicio = document.getElementById('fecha-inicio').value;
        const fechaFin = document.getElementById('fecha-fin').value;

        // Validación básica
        if (fechaInicio && fechaFin && new Date(fechaInicio) > new Date(fechaFin)) {
            alert('La fecha de inicio no puede ser mayor a la fecha final');
            return;
        }


        let url = api_servicios_tipo;
        const params = new URLSearchParams();

        if (fechaInicio) params.append('fecha_inicio', fechaInicio);
        if (fechaFin) params.append('fecha_fin', fechaFin);

        if (params.toString()) url += `?${params.toString()}`;
        // Si no hay fechas, se obtienen todos los registros
        console.log('URL de la API:', url); // Para depuración

        const response = await fetchWithLoader(url);
        const data = await response;
        console.log('Datos obtenidos:', data);
        const mapeoIds = {
            // Hechos Viales
            'colisiones': 'Colisiones',
            'volvamientos': 'Volcamientos',
            'colisiondemotos': 'Colision De Motos',
            'atencionesparamedicas': 'Atenciones Paramedicas',
            'accidentesdetransito': 'Accidentes De Transito - Otros',
            'colisiondevehdecarga': 'Colision De Veh. De Carga',
            'vehiculoqueacealvacio': 'Vehiculo Que Cae Al Vacio',
            'colisionentrevechiculoymoto': 'Colision Entre Vehiculo Y Moto',

            // Consultas Medicas
            'otrosserviciosnoespecificados': 'Otros Servicios No-Señalados',

            // Operaciones, Comunicaciones
            'falsaalarma': 'Falsa Alarma',
            'apoyoinstitucional': 'Apoyo Institucional',
            'atendidonoefectuado': 'Atendido No Efectuado',
            'apoyoconplantaelectrica': 'Apoyo Con Planta Electrica',

            // Rescates
            'rescateenmonta': 'Rescate En Montaña',
            'personaextraviada': 'Persona Extraviada',
            'rescatedepersona': 'Rescate De Persona',
            'rescatedeanimales': 'Rescate De Animales',
            'rescateenelmetro': 'Rescate En El Metro',
            'rescateenascensores': 'Rescate En Ascensores',
            'rescateenestructuras': 'Rescate En Estructuras',
            'rescatepacientepsiquiatrico': 'Rescate Paciente Psiquiatrico',

            // Himenopteros
            'exterminioabejas': 'Exterminio De Abejas',
            'inspeccionesheminopteros': 'Inspeccion Exterminio De Abejas',

            // Abordajes A Comunidades Traslados Con Ambulacia
            'trasladogestante': 'Traslado Gestante',
            'preparacioncomunitaria': 'Preparacion Comunitaria',
            'trasladosenambulancia': 'Traslado En Ambulancia',
            'trasladosinterhospitalario': 'Traslado Interhospitalario',

            // Atenciones Prehospitalarias - Verificacion De Signos Vitales
            'personaherida': 'Persona Herida',
            'nebulizaciones': 'Nebulizaciones',
            'tomadetension': 'Toma De Tension',
            'atencionesparamedicas': 'Atenciones Paramedicas',
            'mordeduradeserpiente': 'Mordedura De Serpiente',
            'soportebasicodevida': 'Soporte Basico De Vida',
            'fallecidoporinmersion': 'Fallecido Por Inmersion',
            'fallecidoporarmablanca': 'Fallecido Por Arma Blanca',
            'fallecidoporarmadefuego': 'Fallecido Por Arma De Fuego',
            'fallecidoenaccidenteaereo': 'Fallecido En Accidente Aereo',
            'inspeccionapersonafallecida': 'Inspeccion A Persona Fallecida',
            'fallecidoenaccidentedetransito': 'Fallecido En Accidente De Transito',

            // Servicios Especiales (Suministros, Apoyo Inst)
            'achicamiento': 'Achicamiento',
            'servicioespecial': 'Servicio Especial',
            'apoyoInstitucional': 'Apoyo Institucional',
            'abastecimientoagua': 'Abastecimiento De Agua',
            'dispersiondeparticulas': 'Dispersion De Particulas',
            'desinfeccionbiologicaporcovid': 'Desinfeccion Biologica Por Covid-19',

            // Pov Apostamientos
            'puestodeavanzadas': 'Puesto De Avanzadas',
            'guardiasdeprevencion': 'Guardias De Prevencion',
            'puestosdeatencionreligiosos': 'Puestos De Atencion En Templos Religiosos',

            // Inspecciones A Establecimientos Comerciales - Investigacion
            'prevencionyseguridad': 'Prevencion Y Seguridad',
            'investigaciondeServicios': 'Investigacion De Servicios',

            // Inspecciones A Zonas De Riesgo
            'desalojos': 'Desalojo',
            'derrumbes': 'Derrumbes',
            'deslizamiento': 'Deslizamiento',
            'evaluacionderiesgo': 'Evaluacion De Riesgo',
            'inpecciontalaarbol': 'Inspeccion Tala De Arbol',

            // Incendios (Estructurales, Forestales, Desechos, Vegetacion, GLP, Derrame De Combustible)
            'reignicion': 'Reignicion',
            'explosiones': 'Explosiones',
            'escapedegas': 'Escape De Gas',
            'conatodeincendio': 'Conato De Incendio',
            'incendiosdebasura': 'Incendios De Basura',
            'incendiosforestales': 'Incendios Forestales',
            'incendiosdevehiculos': 'Incendios En Vehiculos',
            'derramedecombustible': 'Derrame De Combustible',
            'incesdiosenestructuras': 'Incendios En Estructuras',
            'incendiosdeembarcacion': 'Incendio De Embarcacion',
            'incendiosenequiposelectricos': 'Incendios Equipos Electricos',
            'incendiosenvertederosdebasura': 'Incendios En Vertederos De Basura',
            'incendiosporartificiospirotecnicos': 'Incendios Por Artificios Pirotecnicos',

            // Talas, podas
            'taladearbol': 'Tala De Arbol',

            // Capacitacion Practica Bomberil
            'practicabomberil': 'Practica Bomberil',


        };

        Object.keys(mapeoIds).forEach(id => {
            const elemento = document.getElementById(id);
            const nombreServicio = mapeoIds[id];
            if (elemento && data[nombreServicio] !== undefined) {
                elemento.textContent = `(${data[nombreServicio]})`; // Muestra la suma directa
            } else if (elemento) {
                elemento.textContent = "(0)"; // Valor por defecto si no existe
            }
        });

        calcularTotales(data);
    } catch (error) {
        console.error('Error:', error);
    }

    function calcularTotales(data) {
        // Hechos Viales
        const hechosViales = [
            data['Colisiones'] || 0,
            data['Volcamientos'] || 0,
            data['Colision De Motos'] || 0,
            data['Atenciones Paramedicas'] || 0,
            data['Accidentes De Transito - Otros'] || 0,
            data['Colision De Veh. De Carga'] || 0,
            data['Vehiculo Que Cae Al Vacio'] || 0,
            data['Colision Entre Vehiculo Y Moto'] || 0
        ];
        const totalHechosViales = hechosViales.reduce((a, b) => a + b, 0);
        document.getElementById('hechosvialestotal').textContent = `(${totalHechosViales})`;

        // Consultas Medicas
        const consultasMedicas = [
            data['Otros Servicios No-Señalados'] || 0
        ];
        const totalConsultasMedicas = consultasMedicas.reduce((a, b) => a + b, 0);
        document.getElementById('consultasmedicastotales').textContent = `(${totalConsultasMedicas})`;

        // Operaciones, Comunicaciones
        const operacionesComunicaciones = [
            data['Falsa Alarma'] || 0,
            data['Apoyo Institucional'] || 0,
            data['Atendido No Efectuado'] || 0,
            data['Apoyo Con Planta Electrica'] || 0
        ];
        const totalOperacionesComunicaciones = operacionesComunicaciones.reduce((a, b) => a + b, 0);
        document.getElementById('operacionescomunicacionespuestosdeavanzadatotales').textContent = `(${totalOperacionesComunicaciones})`;

        // Rescates
        const rescates = [
            data['Rescate En Montaña'] || 0,
            data['Persona Extraviada'] || 0,
            data['Rescate De Persona'] || 0,
            data['Rescate De Animales'] || 0,
            data['Rescate En El Metro'] || 0,
            data['Rescate En Ascensores'] || 0,
            data['Rescate En Estructuras'] || 0,
            data['Rescate Paciente Psiquiatrico'] || 0
        ];
        const totalRescates = rescates.reduce((a, b) => a + b, 0);
        document.getElementById('rescatestotales').textContent = `(${totalRescates})`;

        // Himenopteros
        const himenopteros = [
            data['Exterminio De Abejas'] || 0,
            data['Inspeccion Exterminio De Abejas'] || 0
        ];
        const totalHimenopteros = himenopteros.reduce((a, b) => a + b, 0);
        document.getElementById('heminopterostotales').textContent = `(${totalHimenopteros})`;
        //    ==============================================
        // Abordajes A Comunidades Traslados Con Ambulacia
        //    ==============================================

        const abordajesComunidadesTrasladosConAmbulancia = [
            data['Traslado Gestante'] || 0,
            data['Preparacion Comunitaria'] || 0,
            data['Traslado En Ambulancia'] || 0,
            data['Traslado Interhospitalario'] || 0,
        ];
        const totalabordajescomunidadestrasladosconambulancia = abordajesComunidadesTrasladosConAmbulancia.reduce((a, b) => a + b, 0);
        document.getElementById('abordajescomunidadestrasladosambulancia').textContent = `(${totalabordajescomunidadestrasladosconambulancia})`;

        // Atenciones Prehospitalarias - Verificacion De Signos Vitales
        const atencionesPrehospitalariasVerificacionDeSignosVitales = [
            data['Persona Herida'] || 0,
            data['Nebulizaciones'] || 0,
            data['Toma De Tension'] || 0,
            data['Atenciones Paramedicas'] || 0,
            data['Mordedura De Serpiente'] || 0,
            data['Soporte Basico De Vida'] || 0,
            data['Fallecido Por Inmersion'] || 0,
            data['Fallecido Por Arma Blanca'] || 0,
            data['Fallecido Por Arma De Fuego'] || 0,
            data['Fallecido En Accidente Aereo'] || 0,
            data['Inspeccion A Persona Fallecida'] || 0,
            data['Fallecido En Accidente De Transito'] || 0,
        ];
        const totalatencionesprehospitalariasverificaciondesignosvitales = atencionesPrehospitalariasVerificacionDeSignosVitales.reduce((a, b) => a + b, 0);
        document.getElementById('atencionesprehospitalariasverificaciondesignostotales').textContent = `(${totalatencionesprehospitalariasverificaciondesignosvitales})`;
        //    =============================================    
        // Servicios Especiales (Suministros, Apoyo Inst)
        //    =============================================

        const serviciosEspecialesTotales = [
            data['Achicamiento'] || 0,
            data['Servicio Especial'] || 0,
            data['Apoyo Institucional'] || 0,
            data['Abastecimiento De Agua'] || 0,
            data['Dispersion De Particulas'] || 0,
            data['Desinfeccion Biologica Por Covid-19'] || 0
        ];
        const totalserviciosespecialestotales = serviciosEspecialesTotales.reduce((a, b) => a + b, 0);
        document.getElementById('serviciosespecialestotales').textContent = `(${totalserviciosespecialestotales})`;

        //    ====================
        // Pov Apostamientos
        //    ====================
        const povapostamientostotales = [
            data['Puesto De Avanzadas'] || 0,
            data['Guardias De Prevencion'] || 0,
            data['Puestos De Atencion En Templos Religiosos'] || 0
        ];
        const totalpovapostamientostotales = povapostamientostotales.reduce((a, b) => a + b, 0);
        document.getElementById('pov-apostamientostotales').textContent = `(${totalpovapostamientostotales})`;

        // ==========================================
        // Inspecciones A Establecimientos Comerciales - Investigacion
        // ==========================================


        const insepccionesestablecimientoscomercialestotales = [
            data['Prevencion Y Seguridad'] || 0,
            data['Investigacion De Servicios'] || 0,
        ];
        const totalinsepccionesestablecimientoscomercialestotales = insepccionesestablecimientoscomercialestotales.reduce((a, b) => a + b, 0);
        document.getElementById('insepccionesestablecimientoscomercialestotales').textContent = `(${totalinsepccionesestablecimientoscomercialestotales})`;

        // ==========================================
        // Inspecciones A Zonas De Riesgo
        // ==========================================


        const inspeccionesazonasderiesgototales = [
            data['Desalojo'] || 0,
            data['Derrumbes'] || 0,
            data['Deslizamiento'] || 0,
            data['Evaluacion De Riesgo'] || 0,
            data['Inspeccion Tala De Arbol'] || 0,
        ];
        const totalinspeccionesazonasderiesgototales = inspeccionesazonasderiesgototales.reduce((a, b) => a + b, 0);
        document.getElementById('inspeccionesazonasderiesgototales').textContent = `(${totalinspeccionesazonasderiesgototales})`;
        // ==========================================        
        // Incendios (Estructurales, Forestales, Desechos, Vegetacion, GLP, Derrame De Combustible)
        // ==========================================

        const incendiosestructuralesglpvegetaciontotales = [
            data['Reignicion'] || 0,
            data['Explosiones'] || 0,
            data['Escape De Gas'] || 0,
            data['Conato De Incendio'] || 0,
            data['Incendios De Basura'] || 0,
            data['Incendios Forestales'] || 0,
            data['Incendios En Vehiculos'] || 0,
            data['Derrame De Combustible'] || 0,
            data['Incendios En Estructuras'] || 0,
            data['Incendio De Embarcacion'] || 0,
            data['Incendios Equipos Electricos'] || 0,
            data['Incendios En Vertederos De Basura'] || 0,
            data['Incendios Por Artificios Pirotecnicos'] || 0
        ];
        const totalincendiosestructuralesglpvegetaciontotales = incendiosestructuralesglpvegetaciontotales.reduce((a, b) => a + b, 0);
        document.getElementById('incendiosestructuralesglpvegetaciontotales').textContent = `(${totalincendiosestructuralesglpvegetaciontotales})`;
        // ==========================================
        // Talas Podas
        // ==========================================

        const talaspodastotales = [
            data['Tala De Arbol'] || 0,
        ];
        const totaltalaspodastotales = talaspodastotales.reduce((a, b) => a + b, 0);
        document.getElementById('talaspodastotales').textContent = `(${totaltalaspodastotales})`;

        // ==========================================
        // Capacitacion Practica Bomberil
        // ==========================================

        const capacitacionpracticabomberiltotales = [
            data['Practica Bomberil'] || 0,
        ];
        const totalcapacitacionpracticabomberiltotales = capacitacionpracticabomberiltotales.reduce((a, b) => a + b, 0);
        document.getElementById('capacitacionpracticabomberiltotales').textContent = `(${totalcapacitacionpracticabomberiltotales})`;


        // Calcular suma total de todos los servicios
        const totalGeneral =
            totalHechosViales +
            totalConsultasMedicas +
            totalOperacionesComunicaciones +
            totalRescates +
            totalHimenopteros +
            totalabordajescomunidadestrasladosconambulancia +
            totalatencionesprehospitalariasverificaciondesignosvitales +
            totalserviciosespecialestotales +
            totalpovapostamientostotales +
            totalinsepccionesestablecimientoscomercialestotales +
            totalinspeccionesazonasderiesgototales +
            totalincendiosestructuralesglpvegetaciontotales +
            totaltalaspodastotales +
            totalcapacitacionpracticabomberiltotales;

        // Actualizar el elemento con la suma total
        document.getElementById('resultadostotales').textContent = `(${totalGeneral})`;

        // ==============
        // // fin script
        // ==============

    }
}

function limpiarFiltro() {
    document.getElementById('fecha-inicio').value = '';
    document.getElementById('fecha-fin').value = '';
    obtenerServicios();
}

// Función auxiliar para obtener número de semana (ISO)
function getWeekNumber(d) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    return [d.getUTCFullYear(), weekNo];
}