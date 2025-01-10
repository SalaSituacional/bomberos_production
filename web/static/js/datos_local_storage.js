
document.addEventListener("DOMContentLoaded", function () {
    

// Leer los datos del localStorage
const storedData = localStorage.getItem('fetchedData');
if (storedData) {
    const data = JSON.parse(storedData);

    // Renderizar los datos en la página
    // datos = JSON.stringify(data, null, 2)
    let datos = data
    console.log(datos)

    inputsValor("id_form1-opciones", datos.id_division)
    atributeDisable("id_form1-opciones")

    // Disparar manualmente el evento 'change' para el select de tipo_procedimiento
    const divisionSelect = document.getElementById("id_form1-opciones");
    const event = new Event("change");
    divisionSelect.dispatchEvent(event);
    
    // Ahora actualizamos las opciones basadas en la división seleccionada
    actualizarOpcionesUnidad()
    actualizarOpciones();

    RellenarValores(datos)
    
    // Disparar manualmente el evento 'change' para el select de tipo_procedimiento
    const tipoProcedimientoSelect = document.getElementById("id_form4-tipo_procedimiento");
    atributeDisable("id_form4-tipo_procedimiento")
    tipoProcedimientoSelect.dispatchEvent(event);
    
    const dependenciaSelect = document.getElementById("id_form_capacitacion-dependencia");
    dependenciaSelect.dispatchEvent(event);
    
    const solicitanteSelect = document.getElementById("id_form2-solicitante");
    solicitanteSelect.dispatchEvent(event);

    document.getElementById("id_atenciones_paramedicas-tipo_atencion").dispatchEvent(event)
    document.getElementById("id_emergencias_medicas-trasladado").dispatchEvent(event)
    document.getElementById("id_formulario_accidentes_transito-agg_vehiculo").dispatchEvent(event)
    document.getElementById("id_detalles_vehiculos_accidentes-agg_vehiculo").dispatchEvent(event)
    document.getElementById("id_detalles_vehiculos_accidentes2-agg_vehiculo").dispatchEvent(event)
    document.getElementById("id_formulario_accidentes_transito-agg_lesionado").dispatchEvent(event)
    document.getElementById("id_detalles_lesionados_accidentes-trasladado").dispatchEvent(event)
    document.getElementById("id_detalles_lesionados_accidentes-otro_lesionado").dispatchEvent(event)
    document.getElementById("id_detalles_lesionados_accidentes2-trasladado").dispatchEvent(event)
    document.getElementById("id_detalles_lesionados_accidentes2-otro_lesionado").dispatchEvent(event)
    document.getElementById("id_detalles_lesionados_accidentes3-trasladado").dispatchEvent(event)
    document.getElementById("id_rescate_form-tipo_rescate").dispatchEvent(event)
    document.getElementById("id_incendio_form-tipo_incendio").dispatchEvent(event)
    document.getElementById("id_incendio_form-check_agregar_persona").dispatchEvent(event)
    document.getElementById("id_incendio_form-check_retencion").dispatchEvent(event)
    document.getElementById("id_evaluacion_riesgo_form-tipo_riesgo").dispatchEvent(event)
    document.getElementById("id_form_inspecciones-tipo_inspeccion").dispatchEvent(event)
    document.getElementById("id_form_investigacion-tipo_siniestro").dispatchEvent(event)
    document.getElementById("id_form_brigada-tipo_capacitacion").dispatchEvent(event)
    document.getElementById("id_form_comision-agregar").dispatchEvent(event)
    document.getElementById("id_datos_comision_uno-agregar").dispatchEvent(event)
    document.getElementById("id_datos_comision_dos-agregar").dispatchEvent(event)
    
} else {
    console.error('No se encontraron datos en localStorage.');
}


function RellenarValores(datos) {
    let division = datos.id_division
    inputsValor("id_procedimiento_editar",datos.id)
    const tipo_procedimiento = datos.tipo_procedimiento

    if (division === 1 || division === 2 || division === 4 || division === 5) {
        inputsValor("id_form2-solicitante", datos.solicitante)
        inputsValor("id_form2-solicitante_externo", datos.solicitante_externo)
        inputsValor("id_form2-unidad", datos.unidad)
        inputsValor("id_form2-efectivos_enviados", datos.efectivos)
        inputsValor("id_form2-jefe_comision", datos.jefe_comision)   
        inputsValor("id_form3-municipio", datos.municipio)   
        inputsValor("id_form3-parroquia", datos.parroquia)   
        inputsValor("id_form3-direccion", datos.direccion)   
        inputsValor("id_form3-hora", datos.hora)   
        inputsValor("id_form3-fecha", datos.fecha)   
        inputsValor("id_form4-tipo_procedimiento", datos.tipo_procedimiento)   

        if(datos.comisiones && datos.comisiones.length > 0) {
            RellenarComisiones(datos.comisiones)
        }

    } else if (division === 3) {
        inputsValor("id_form2-solicitante", datos.solicitante)
        inputsValor("id_form2-solicitante_externo", datos.solicitante_externo)
        inputsValor("id_form2-efectivos_enviados", datos.efectivos)
        inputsValor("id_form2-jefe_comision", datos.jefe_comision)   
        inputsValor("id_form3-municipio", datos.municipio)
        inputsValor("id_form3-parroquia", datos.parroquia)   
        inputsValor("id_form3-direccion", datos.direccion)   
        inputsValor("id_form3-hora", datos.hora)   
        inputsValor("id_form3-fecha", datos.fecha)   
        inputsValor("id_form4-tipo_procedimiento", datos.tipo_procedimiento)   

        if(datos.comisiones && datos.comisiones.length > 0) {
            RellenarComisiones(datos.comisiones)
        }

    } else if (division === 6) {
        inputsValor("id_form_enfermeria-dependencia", datos.dependencia)
        inputsValor("id_form_enfermeria-encargado_area", datos.solicitante_externo)
        inputsValor("id_form3-municipio", datos.municipio)
        inputsValor("id_form3-parroquia", datos.parroquia)   
        inputsValor("id_form3-direccion", datos.direccion)   
        inputsValor("id_form3-hora", datos.hora)   
        inputsValor("id_form3-fecha", datos.fecha)   
        inputsValor("id_form4-tipo_procedimiento", datos.tipo_procedimiento)   
    } else if (division === 7) {
        inputsValor("id_form_servicios_medicos-tipo_servicio", datos.tipo_servicio)
        inputsValor("id_form_servicios_medicos-jefe_area", datos.solicitante_externo)
        inputsValor("id_form3-municipio", datos.municipio)
        inputsValor("id_form3-parroquia", datos.parroquia)   
        inputsValor("id_form3-direccion", datos.direccion)   
        inputsValor("id_form3-hora", datos.hora)   
        inputsValor("id_form3-fecha", datos.fecha)   
        inputsValor("id_form4-tipo_procedimiento", datos.tipo_procedimiento)   
    } else if (division === 8) {
        inputsValor("id_form_psicologia-jefe_area", datos.solicitante_externo)
        inputsValor("id_form3-municipio", datos.municipio)
        inputsValor("id_form3-parroquia", datos.parroquia)   
        inputsValor("id_form3-direccion", datos.direccion)   
        inputsValor("id_form3-hora", datos.hora)   
        inputsValor("id_form3-fecha", datos.fecha)   
        inputsValor("id_form4-tipo_procedimiento", datos.tipo_procedimiento)   
    } else if (division === 9) {
        inputsValor("id_form_capacitacion-dependencia", datos.dependencia)
        atributeDisable("id_form_capacitacion-dependencia")
        inputsValor("id_form_capacitacion-instructor", datos.jefe_comision)
        inputsValor("id_form_capacitacion-solicitante", datos.solicitante)
        inputsValor("id_form3-municipio", datos.municipio)
        inputsValor("id_form3-parroquia", datos.parroquia)   
        inputsValor("id_form3-direccion", datos.direccion)   
        inputsValor("id_form3-hora", datos.hora)   
        inputsValor("id_form3-fecha", datos.fecha)   
        inputsValor("id_form4-tipo_procedimiento", datos.tipo_procedimiento)
    }

    RellenarDetalles(datos, tipo_procedimiento)

}

function RellenarComisiones(datos) {
    console.log(datos)

    if (datos[0]) {
        document.getElementById("id_form_comision-agregar").checked = true
        atributeDisable("id_form_comision-agregar")

        inputsValor("id_datos_comision_uno-comision", datos[0].comision)
        inputsValor("id_datos_comision_uno-nombre_oficial", datos[0].nombre_oficial)
        inputsValor("id_datos_comision_uno-apellido_oficial", datos[0].apellido_oficial)
        inputsValor("id_datos_comision_uno-nacionalidad", dividirCedula(datos[0].cedula_oficial)[0])
        inputsValor("id_datos_comision_uno-cedula_oficial", dividirCedula(datos[0].cedula_oficial)[1])
        inputsValor("id_datos_comision_uno-nro_unidad", datos[0].nro_unidad)
        inputsValor("id_datos_comision_uno-nro_cuadrante", datos[0].nro_cuadrante)
        
        if (datos[1]) {
            document.getElementById("id_datos_comision_uno-agregar").checked = true
            atributeDisable("id_datos_comision_uno-agregar")

            inputsValor("id_datos_comision_dos-comision", datos[1].comision)
            inputsValor("id_datos_comision_dos-nombre_oficial", datos[1].nombre_oficial)
            inputsValor("id_datos_comision_dos-apellido_oficial", datos[1].apellido_oficial)
            inputsValor("id_datos_comision_dos-nacionalidad", dividirCedula(datos[1].cedula_oficial)[0])
            inputsValor("id_datos_comision_dos-cedula_oficial", dividirCedula(datos[1].cedula_oficial)[1])
            inputsValor("id_datos_comision_dos-nro_unidad", datos[1].nro_unidad)
            inputsValor("id_datos_comision_dos-nro_cuadrante", datos[1].nro_cuadrante)
            
            if (datos[2]) {
                document.getElementById("id_datos_comision_dos-agregar").checked = true
                atributeDisable("id_datos_comision_dos-agregar")

                inputsValor("id_datos_comision_tres-comision", datos[2].comision)
                inputsValor("id_datos_comision_tres-nombre_oficial", datos[2].nombre_oficial)
                inputsValor("id_datos_comision_tres-apellido_oficial", datos[2].apellido_oficial)
                inputsValor("id_datos_comision_tres-nacionalidad", dividirCedula(datos[2].cedula_oficial)[0])
                inputsValor("id_datos_comision_tres-cedula_oficial", dividirCedula(datos[2].cedula_oficial)[1])
                inputsValor("id_datos_comision_tres-nro_unidad", datos[2].nro_unidad)
                inputsValor("id_datos_comision_tres-nro_cuadrante", datos[2].nro_cuadrante)
                
            }
        }
    } 
}

function RellenarDetalles(datos, tipo_procedimiento) {
    const inf = datos
    
    switch (tipo_procedimiento) {
        case 1:
            inputsValor("id_abast_agua-tipo_servicio", inf.ente_suministrado)
            inputsValor("id_abast_agua-nombres", inf.nombres)
            inputsValor("id_abast_agua-apellidos", inf.apellidos)
            inputsValor("id_abast_agua-nacionalidad", dividirCedula(inf.cedula)[0])
            inputsValor("id_abast_agua-cedula", dividirCedula(inf.cedula)[1])
            inputsValor("id_abast_agua-ltrs_agua", inf.ltrs_agua)
            inputsValor("id_abast_agua-personas_atendidas", inf.personas_atendidas)
            inputsValor("id_abast_agua-descripcion", inf.descripcion)
            inputsValor("id_abast_agua-material_utilizado", inf.material_utilizado)
            inputsValor("id_abast_agua-status", inf.status)
            break;
        
        case 2:
            inputsValor("id_apoyo_unid-tipo_apoyo", inf.tipo_apoyo)
            inputsValor("id_apoyo_unid-unidad_apoyada", inf.unidad_apoyada)
            inputsValor("id_apoyo_unid-descripcion", inf.descripcion)
            inputsValor("id_apoyo_unid-material_utilizado", inf.material_utilizado)
            inputsValor("id_apoyo_unid-status", inf.status)
            break;
        
        case 3:
            inputsValor("id_guard_prev-motivo_prevencion", inf.motivo_prevencion)
            inputsValor("id_guard_prev-descripcion", inf.descripcion)
            inputsValor("id_guard_prev-material_utilizado", inf.material_utilizado)
            inputsValor("id_guard_prev-status", inf.status)
            break;
            
        case 4:
            inputsValor("id_atend_no_efec-descripcion", inf.descripcion)
            inputsValor("id_atend_no_efec-material_utilizado", inf.material_utilizado)
            inputsValor("id_atend_no_efec-status", inf.status)
            break;
                
        case 5:
            inputsValor("id_desp_seguridad-motv_despliegue", inf.motivo_despliegue)
            inputsValor("id_desp_seguridad-descripcion", inf.descripcion)
            inputsValor("id_desp_seguridad-material_utilizado", inf.material_utilizado)
            inputsValor("id_desp_seguridad-status", inf.status)
            break;
        
        case 6:
            inputsValor("id_fals_alarm-motv_alarma", inf.motivo_alarma)
            inputsValor("id_fals_alarm-descripcion", inf.descripcion)
            inputsValor("id_fals_alarm-material_utilizado", inf.material_utilizado)
            inputsValor("id_fals_alarm-status", inf.status)
            break;
        
        case 7:
            inputsValor("id_atenciones_paramedicas-tipo_atencion", inf.tipo_atencion)
            if (inf.tipo_atencion === "Emergencias Medicas") {
                inputsValor("id_emergencias_medicas-nombre", inf.nombres)
                inputsValor("id_emergencias_medicas-apellido", inf.apellidos)
                inputsValor("id_emergencias_medicas-nacionalidad", dividirCedula(inf.cedula)[0])
                inputsValor("id_emergencias_medicas-cedula", dividirCedula(inf.cedula)[1])
                inputsValor("id_emergencias_medicas-edad", inf.edad)
                inputsValor("id_emergencias_medicas-sexo", inf.sexo)
                inputsValor("id_emergencias_medicas-idx", inf.idx)
                inputsValor("id_emergencias_medicas-descripcion", inf.descripcion)
                inputsValor("id_emergencias_medicas-material_utilizado", inf.material_utilizado)
                inputsValor("id_emergencias_medicas-status", inf.status)
                if (inf.traslado == true) {
                    document.getElementById("id_emergencias_medicas-trasladado").checked = true
                    inputsValor("id_traslados_emergencias-hospital_trasladado", inf.hospital)
                    inputsValor("id_traslados_emergencias-medico_receptor", inf.medico)
                    inputsValor("id_traslados_emergencias-mpps_cmt", inf.mpps_cmt)
                }
            } else {
                inputsValor("id_formulario_accidentes_transito-tipo_accidente", inf.tipo_accidente)
                inputsValor("id_formulario_accidentes_transito-cantidad_lesionado", inf.cantidad_lesionados)
                inputsValor("id_formulario_accidentes_transito-material_utilizado", inf.material_utilizado)
                inputsValor("id_formulario_accidentes_transito-status", inf.status)
                
                if (inf.vehiculos[0]) {
                    document.getElementById("id_formulario_accidentes_transito-agg_vehiculo").checked = true
                    inputsValor("id_detalles_vehiculos_accidentes-modelo", inf.vehiculos[0].modelo)
                    inputsValor("id_detalles_vehiculos_accidentes-marca", inf.vehiculos[0].marca)
                    inputsValor("id_detalles_vehiculos_accidentes-color", inf.vehiculos[0].color)
                    inputsValor("id_detalles_vehiculos_accidentes-año", inf.vehiculos[0].año)
                    inputsValor("id_detalles_vehiculos_accidentes-placas", inf.vehiculos[0].placas)
                    
                    if (inf.vehiculos[1]) {
                        document.getElementById("id_detalles_vehiculos_accidentes-agg_vehiculo").checked = true
                        inputsValor("id_detalles_vehiculos_accidentes2-modelo", inf.vehiculos[1].modelo)
                        inputsValor("id_detalles_vehiculos_accidentes2-marca", inf.vehiculos[1].marca)
                        inputsValor("id_detalles_vehiculos_accidentes2-color", inf.vehiculos[1].color)
                        inputsValor("id_detalles_vehiculos_accidentes2-año", inf.vehiculos[1].año)
                        inputsValor("id_detalles_vehiculos_accidentes2-placas", inf.vehiculos[1].placas)

                        if (inf.vehiculos[2]) {
                            document.getElementById("id_detalles_vehiculos_accidentes2-agg_vehiculo").checked = true
                            inputsValor("id_detalles_vehiculos_accidentes3-modelo", inf.vehiculos[2].modelo)
                            inputsValor("id_detalles_vehiculos_accidentes3-marca", inf.vehiculos[2].marca)
                            inputsValor("id_detalles_vehiculos_accidentes3-color", inf.vehiculos[2].color)
                            inputsValor("id_detalles_vehiculos_accidentes3-año", inf.vehiculos[2].año)
                            inputsValor("id_detalles_vehiculos_accidentes3-placas", inf.vehiculos[2].placas)
                        }
                    }
                }
                
                if (inf.lesionados[0]) {
                    document.getElementById("id_formulario_accidentes_transito-agg_lesionado").checked = true
                    inputsValor("id_detalles_lesionados_accidentes-nombre", inf.lesionados[0].nombre)
                    inputsValor("id_detalles_lesionados_accidentes-apellido", inf.lesionados[0].apellidos)
                    inputsValor("id_detalles_lesionados_accidentes-nacionalidad", dividirCedula(inf.lesionados[0].cedula)[0])
                    inputsValor("id_detalles_lesionados_accidentes-cedula", dividirCedula(inf.lesionados[0].cedula)[1])
                    inputsValor("id_detalles_lesionados_accidentes-edad", inf.lesionados[0].edad)
                    inputsValor("id_detalles_lesionados_accidentes-sexo", inf.lesionados[0].sexo)
                    inputsValor("id_detalles_lesionados_accidentes-idx", inf.lesionados[0].idx)
                    inputsValor("id_detalles_lesionados_accidentes-descripcion", inf.lesionados[0].descripcion)
                    
                    if (inf.lesionados[0].traslados[0]) {
                        document.getElementById("id_detalles_lesionados_accidentes-trasladado").checked = true
                        inputsValor("id_traslados_accidentes-hospital_trasladado", inf.lesionados[0].traslados[0].hospital)
                        inputsValor("id_traslados_accidentes-medico_receptor", inf.lesionados[0].traslados[0].medico)
                        inputsValor("id_traslados_accidentes-mpps_cmt", inf.lesionados[0].traslados[0].mpps_cmt)   
                    }
                    
                    if (inf.lesionados[1]) {
                        document.getElementById("id_detalles_lesionados_accidentes-otro_lesionado").checked = true
                        inputsValor("id_detalles_lesionados_accidentes2-nombre", inf.lesionados[1].nombre)
                        inputsValor("id_detalles_lesionados_accidentes2-apellido", inf.lesionados[1].apellidos)
                        inputsValor("id_detalles_lesionados_accidentes2-nacionalidad", dividirCedula(inf.lesionados[1].cedula)[0])
                        inputsValor("id_detalles_lesionados_accidentes2-cedula", dividirCedula(inf.lesionados[1].cedula)[1])
                        inputsValor("id_detalles_lesionados_accidentes2-edad", inf.lesionados[1].edad)
                        inputsValor("id_detalles_lesionados_accidentes2-sexo", inf.lesionados[1].sexo)
                        inputsValor("id_detalles_lesionados_accidentes2-idx", inf.lesionados[1].idx)
                        inputsValor("id_detalles_lesionados_accidentes2-descripcion", inf.lesionados[1].descripcion)
                        
                        if (inf.lesionados[1].traslados[0]) {
                            document.getElementById("id_detalles_lesionados_accidentes2-trasladado").checked = true
                            inputsValor("id_traslados_accidentes2-hospital_trasladado", inf.lesionados[1].traslados[0].hospital)
                            inputsValor("id_traslados_accidentes2-medico_receptor", inf.lesionados[1].traslados[0].medico)
                            inputsValor("id_traslados_accidentes2-mpps_cmt", inf.lesionados[1].traslados[0].mpps_cmt)   
                        }
                        
                        if (inf.lesionados[2]) {
                            document.getElementById("id_detalles_lesionados_accidentes2-otro_lesionado").checked = true
                            inputsValor("id_detalles_lesionados_accidentes3-nombre", inf.lesionados[2].nombre)
                            inputsValor("id_detalles_lesionados_accidentes3-apellido", inf.lesionados[2].apellidos)
                            inputsValor("id_detalles_lesionados_accidentes3-nacionalidad", dividirCedula(inf.lesionados[2].cedula)[0])
                            inputsValor("id_detalles_lesionados_accidentes3-cedula", dividirCedula(inf.lesionados[2].cedula)[1])
                            inputsValor("id_detalles_lesionados_accidentes3-edad", inf.lesionados[2].edad)
                            inputsValor("id_detalles_lesionados_accidentes3-sexo", inf.lesionados[2].sexo)
                            inputsValor("id_detalles_lesionados_accidentes3-idx", inf.lesionados[2].idx)
                            inputsValor("id_detalles_lesionados_accidentes3-descripcion", inf.lesionados[2].descripcion)
                            
                            if (inf.lesionados[2].traslados[0]) {
                                document.getElementById("id_detalles_lesionados_accidentes3-trasladado").checked = true
                                inputsValor("id_traslados_accidentes3-hospital_trasladado", inf.lesionados[2].traslados[0].hospital)
                                inputsValor("id_traslados_accidentes3-medico_receptor", inf.lesionados[2].traslados[0].medico)
                                inputsValor("id_traslados_accidentes3-mpps_cmt", inf.lesionados[2].traslados[0].mpps_cmt)   
                            }
                            
                        }
                    }
                    
                    // if (inf.vehiculos[1]) {
                    //     document.getElementById("id_detalles_vehiculos_accidentes-agg_vehiculo").checked = true
                    //     inputsValor("id_detalles_vehiculos_accidentes2-modelo", inf.vehiculos[1].modelo)
                    //     inputsValor("id_detalles_vehiculos_accidentes2-marca", inf.vehiculos[1].marca)
                    //     inputsValor("id_detalles_vehiculos_accidentes2-color", inf.vehiculos[1].color)
                    //     inputsValor("id_detalles_vehiculos_accidentes2-año", inf.vehiculos[1].año)
                    //     inputsValor("id_detalles_vehiculos_accidentes2-placas", inf.vehiculos[1].placas)

                    //     if (inf.vehiculos[2]) {
                    //         document.getElementById("id_detalles_vehiculos_accidentes2-agg_vehiculo").checked = true
                    //         inputsValor("id_detalles_vehiculos_accidentes3-modelo", inf.vehiculos[2].modelo)
                    //         inputsValor("id_detalles_vehiculos_accidentes3-marca", inf.vehiculos[2].marca)
                    //         inputsValor("id_detalles_vehiculos_accidentes3-color", inf.vehiculos[2].color)
                    //         inputsValor("id_detalles_vehiculos_accidentes3-año", inf.vehiculos[2].año)
                    //         inputsValor("id_detalles_vehiculos_accidentes3-placas", inf.vehiculos[2].placas)
                    //     }
                    // }
                }
            }

            break;

        case 9:
            inputsValor("id_serv_especial-tipo_servicio", inf.tipo_servicio)
            inputsValor("id_serv_especial-descripcion", inf.descripcion)
            inputsValor("id_serv_especial-material_utilizado", inf.material_utilizado)
            inputsValor("id_serv_especial-status", inf.status)
            break;

        case 10:
            inputsValor("id_rescate_form-tipo_rescate", inf.tipo_rescate)
            inputsValor("id_rescate_form-material_utilizado", inf.material_utilizado)
            inputsValor("id_rescate_form-status", inf.status)
            
            if (inf.tipo_rescate === 1) {
                inputsValor("id_rescate_form_animal-especie", inf.especie)
                inputsValor("id_rescate_form_animal-descripcion", inf.descripcion)
            } else {
                inputsValor("id_rescate_form_persona-nombre_persona", inf.nombres)
                inputsValor("id_rescate_form_persona-apellido_persona", inf.apellidos)
                inputsValor("id_rescate_form_persona-nacionalidad", dividirCedula(inf.cedula)[0])
                inputsValor("id_rescate_form_persona-cedula_persona", dividirCedula(inf.cedula)[1])
                inputsValor("id_rescate_form_persona-edad_persona", inf.edad)
                inputsValor("id_rescate_form_persona-sexo_persona", inf.sexo)
                inputsValor("id_rescate_form_persona-descripcion", inf.descripcion)
            }

            break;
            
        case 11:
            inputsValor("id_incendio_form-tipo_incendio", inf.tipo_incendio)
            inputsValor("id_incendio_form-material_utilizado", inf.material_utilizado)
            inputsValor("id_incendio_form-status", inf.status)
            inputsValor("id_incendio_form-descripcion", inf.descripcion)
            
            if (inf.persona) {
                document.getElementById("id_incendio_form-check_agregar_persona").checked = true
                inputsValor("id_persona_presente_form-nombre", inf.nombre)
                inputsValor("id_persona_presente_form-apellido", inf.nombre)
                inputsValor("id_persona_presente_form-nacionalidad", dividirCedula(inf.cedula)[0])
                inputsValor("id_persona_presente_form-cedula", dividirCedula(inf.cedula)[1])
                inputsValor("id_persona_presente_form-edad", inf.edad)
            }
            
            if (inf.retencion) {
                document.getElementById("id_incendio_form-check_retencion").checked = true
                if (inf.tipo_cilindro === "Oxigeno") {
                    inf.tipo_cilindro = 2
                } else if (inf.tipo_cilindro === "GLP"){
                    inf.tipo_cilindro = 1
                } else {
                    inf.tipo_cilindro = 3
                }
                inputsValor("id_retencion_preventiva_incendio-tipo_cilindro", inf.tipo_cilindro)
                inputsValor("id_retencion_preventiva_incendio-capacidad", inf.capacidad)
                inputsValor("id_retencion_preventiva_incendio-serial", inf.serial)
                inputsValor("id_retencion_preventiva_incendio-nro_constancia_retencion", inf.nro_constancia)
                inputsValor("id_retencion_preventiva_incendio-nombre", inf.nombre)
                inputsValor("id_retencion_preventiva_incendio-apellidos", inf.apellidos)
                inputsValor("id_retencion_preventiva_incendio-nacionalidad", dividirCedula(inf.cedula)[0])
                inputsValor("id_retencion_preventiva_incendio-cedula", dividirCedula(inf.cedula)[1])
                
            }

            break;
        
        case 12:
            inputsValor("id_form_fallecido-motivo_fallecimiento", inf.motivo_fallecimiento)
            inputsValor("id_form_fallecido-nom_fallecido", inf.nombres)
            inputsValor("id_form_fallecido-apellido_fallecido", inf.apellidos)
            inputsValor("id_form_fallecido-nacionalidad", dividirCedula(inf.cedula)[0])
            inputsValor("id_form_fallecido-cedula_fallecido", dividirCedula(inf.cedula)[1])
            inputsValor("id_form_fallecido-edad", inf.edad)
            inputsValor("id_form_fallecido-sexo", inf.sexo)
            inputsValor("id_form_fallecido-descripcion", inf.descripcion)
            inputsValor("id_form_fallecido-material_utilizado", inf.material_utilizado)
            inputsValor("id_form_fallecido-status", inf.status)
            break;

        case 13:
            inputsValor("id_mitigacion_riesgo_form-tipo_riesgo", inf.tipo_servicio)
            inputsValor("id_mitigacion_riesgo_form-descripcion", inf.descripcion)
            inputsValor("id_mitigacion_riesgo_form-material_utilizado", inf.material_utilizado)
            inputsValor("id_mitigacion_riesgo_form-status", inf.status)
            break;

        case 14:
            inputsValor("id_evaluacion_riesgo_form-tipo_riesgo", inf.tipo_de_evaluacion)
            inputsValor("id_evaluacion_riesgo_form-descripcion", inf.descripcion)
            inputsValor("id_evaluacion_riesgo_form-material_utilizado", inf.material_utilizado)
            inputsValor("id_evaluacion_riesgo_form-status", inf.status)

            if (inf.id_division === 3 ){
                inputsValor("id_persona_presente_eval_form-nombre", inf.nombre)
                inputsValor("id_persona_presente_eval_form-apellidos", inf.apellido)
                inputsValor("id_persona_presente_eval_form-nacionalidad", dividirCedula(inf.cedula)[0])
                inputsValor("id_persona_presente_eval_form-cedula", dividirCedula(inf.cedula)[1])
                inputsValor("id_persona_presente_eval_form-telefono", inf.telefono)
            }
            
            if (inf.tipo_estructura) {
                inputsValor("id_evaluacion_riesgo_form-tipo_etructura", inf.tipo_estructura)
            }

            break;
            
        case 15:
            inputsValor("id_puesto_avanzada_form-tipo_avanzada", inf.tipo_de_servicio)
            inputsValor("id_puesto_avanzada_form-descripcion", inf.descripcion)
            inputsValor("id_puesto_avanzada_form-material_utilizado", inf.material_utilizado)
            inputsValor("id_puesto_avanzada_form-status", inf.status)

            break;
        
        case 16:
            inputsValor("id_traslados_prehospitalaria_form-tipo_traslado", inf.traslado)
            inputsValor("id_traslados_prehospitalaria_form-descripcion", inf.descripcion)
            inputsValor("id_traslados_prehospitalaria_form-material_utilizado", inf.material_utilizado)
            inputsValor("id_traslados_prehospitalaria_form-status", inf.status)
            inputsValor("id_traslados_prehospitalaria_form-nombre", inf.nombre)
            inputsValor("id_traslados_prehospitalaria_form-apellido", inf.apellido)
            inputsValor("id_traslados_prehospitalaria_form-nacionalidad", dividirCedula(inf.cedula)[0])
            inputsValor("id_traslados_prehospitalaria_form-cedula", dividirCedula(inf.cedula)[1])
            inputsValor("id_traslados_prehospitalaria_form-edad", inf.edad)
            inputsValor("id_traslados_prehospitalaria_form-sexo", inf.sexo)
            inputsValor("id_traslados_prehospitalaria_form-idx", inf.idx)
            inputsValor("id_traslados_prehospitalaria_form-hospital_trasladado", inf.hospital)
            inputsValor("id_traslados_prehospitalaria_form-medico_receptor", inf.medico)
            inputsValor("id_traslados_prehospitalaria_form-mpps_cmt", inf.mpps)
            break;

        case 17:
            inputsValor("id_asesoramiento_form-nombre_comercio", inf.nombre_comercio)
            inputsValor("id_asesoramiento_form-rif_comercio", inf.rif_comercio)
            inputsValor("id_asesoramiento_form-nombres", inf.nombre)
            inputsValor("id_asesoramiento_form-apellidos", inf.apellido)
            inputsValor("id_asesoramiento_form-nacionalidad", dividirCedula(inf.cedula)[0])
            inputsValor("id_asesoramiento_form-cedula", dividirCedula(inf.cedula)[1])
            inputsValor("id_asesoramiento_form-sexo", inf.sexo)
            inputsValor("id_asesoramiento_form-telefono", inf.telefono)
            inputsValor("id_asesoramiento_form-descripcion", inf.descripcion)
            inputsValor("id_asesoramiento_form-material_utilizado", inf.material_utilizado)
            inputsValor("id_asesoramiento_form-status", inf.status)
            break;
        
        case 18:
            inputsValor("id_form_inspecciones-tipo_inspeccion", inf.tipo_inspeccion)

            if (inf.tipo_inspeccion === "Prevención" || inf.tipo_inspeccion === "Asesorias Tecnicas") {
                inputsValor("id_form_inspecciones_prevencion-nombre_comercio", inf.nombre_comercio)
                inputsValor("id_form_inspecciones_prevencion-propietario", inf.propietario)
                inputsValor("id_form_inspecciones_prevencion-nacionalidad", dividirCedula(inf.cedula_propietario)[0])
                inputsValor("id_form_inspecciones_prevencion-cedula_propietario", dividirCedula(inf.cedula_propietario)[1])
                inputsValor("id_form_inspecciones_prevencion-descripcion", inf.descripcion)
                inputsValor("id_form_inspecciones_prevencion-persona_sitio_nombre", inf.persona_sitio_nombre)
                inputsValor("id_form_inspecciones_prevencion-persona_sitio_apellido", inf.persona_sitio_apellido)
                inputsValor("id_form_inspecciones_prevencion-nacionalidad2", dividirCedula(inf.persona_sitio_cedula)[0])
                inputsValor("id_form_inspecciones_prevencion-persona_sitio_cedula", dividirCedula(inf.persona_sitio_cedula)[1])
                inputsValor("id_form_inspecciones_prevencion-persona_sitio_telefono", inf.persona_sitio_telefono)
                inputsValor("id_form_inspecciones_prevencion-material_utilizado", inf.material_utilizado)
                inputsValor("id_form_inspecciones_prevencion-status", inf.status)

            } else if (inf.tipo_inspeccion === "Habitabilidad") {
                inputsValor("id_form_inspecciones_habitabilidad-descripcion", inf.descripcion)
                inputsValor("id_form_inspecciones_habitabilidad-persona_sitio_nombre", inf.persona_sitio_nombre)
                inputsValor("id_form_inspecciones_habitabilidad-persona_sitio_apellido", inf.persona_sitio_apellido)
                inputsValor("id_form_inspecciones_habitabilidad-nacionalidad", dividirCedula(inf.persona_sitio_cedula)[0])
                inputsValor("id_form_inspecciones_habitabilidad-persona_sitio_cedula", dividirCedula(inf.persona_sitio_cedula)[1])
                inputsValor("id_form_inspecciones_habitabilidad-persona_sitio_telefono", inf.persona_sitio_telefono)
                inputsValor("id_form_inspecciones_habitabilidad-material_utilizado", inf.material_utilizado)
                inputsValor("id_form_inspecciones_habitabilidad-status", inf.status)
                
            } else if (inf.tipo_inspeccion === "Otros") {
                inputsValor("id_form_inspecciones_otros-especifique", inf.especifique)                
                inputsValor("id_form_inspecciones_otros-descripcion", inf.descripcion)                
                inputsValor("id_form_inspecciones_otros-persona_sitio_nombre", inf.persona_sitio_nombre)                
                inputsValor("id_form_inspecciones_otros-persona_sitio_apellido", inf.persona_sitio_apellido)                
                inputsValor("id_form_inspecciones_otros-nacionalidad", dividirCedula(inf.persona_sitio_cedula)[0])                
                inputsValor("id_form_inspecciones_otros-persona_sitio_cedula", dividirCedula(inf.persona_sitio_cedula)[1])                
                inputsValor("id_form_inspecciones_otros-persona_sitio_telefono", inf.persona_sitio_telefono)                
                inputsValor("id_form_inspecciones_otros-material_utilizado", inf.material_utilizado)                
                inputsValor("id_form_inspecciones_otros-status", inf.status)                

            } else if (inf.tipo_inspeccion === "Árbol") {
                inputsValor("id_form_inspecciones_arbol-especie", inf.especie)
                inputsValor("id_form_inspecciones_arbol-altura_aprox", inf.altura_aprox)
                inputsValor("id_form_inspecciones_arbol-ubicacion_arbol", inf.ubicacion_arbol)
                inputsValor("id_form_inspecciones_arbol-descripcion", inf.descripcion)
                inputsValor("id_form_inspecciones_arbol-persona_sitio_nombre", inf.persona_sitio_nombre)
                inputsValor("id_form_inspecciones_arbol-persona_sitio_apellido", inf.persona_sitio_apellido)
                inputsValor("id_form_inspecciones_arbol-nacionalidad", dividirCedula(inf.persona_sitio_cedula)[0])
                inputsValor("id_form_inspecciones_arbol-persona_sitio_cedula", dividirCedula(inf.persona_sitio_cedula)[1])
                inputsValor("id_form_inspecciones_arbol-persona_sitio_telefono", inf.persona_sitio_telefono)
                inputsValor("id_form_inspecciones_arbol-material_utilizado", inf.material_utilizado)
                inputsValor("id_form_inspecciones_arbol-status", inf.status)
                
            }


            break;

        case 19:
            inputsValor("id_form_investigacion-tipo_investigacion", inf.tipo_investigacion)
            inputsValor("id_form_investigacion-tipo_siniestro", inf.tipo_siniestro)
            
            if (inf.tipo_siniestro=="Estructura" || inf.tipo_siniestro=="Vivienda") {
                inputsValor("id_form_inv_estructura-tipo_estructura", inf.tipo_estructura)
                inputsValor("id_form_inv_estructura-nombre", inf.nombre_propietario_estructura)
                inputsValor("id_form_inv_estructura-apellido", inf.apellido_propietario_estructura)
                inputsValor("id_form_inv_estructura-nacionalidad", dividirCedula(inf.cedula_propietario_estructura)[0])
                inputsValor("id_form_inv_estructura-cedula", dividirCedula(inf.cedula_propietario_estructura)[1])
                inputsValor("id_form_inv_estructura-descripcion", inf.descripcion_estructura)
                inputsValor("id_form_inv_estructura-material_utilizado", inf.material_utilizado_estructura)
                inputsValor("id_form_inv_estructura-status", inf.status_estructura)

            } else if (inf.tipo_siniestro=="Vehiculo") {
                inputsValor("id_form_inv_vehiculo-marca", inf.marca)
                inputsValor("id_form_inv_vehiculo-modelo", inf.modelo)
                inputsValor("id_form_inv_vehiculo-color", inf.color)
                inputsValor("id_form_inv_vehiculo-placas", inf.placas)
                inputsValor("id_form_inv_vehiculo-año", inf.año)
                inputsValor("id_form_inv_vehiculo-nombre_propietario", inf.nombre_propietario)
                inputsValor("id_form_inv_vehiculo-apellido_propietario", inf.apellido_propietario)
                inputsValor("id_form_inv_vehiculo-nacionalidad", dividirCedula(inf.cedula_propietario)[0])
                inputsValor("id_form_inv_vehiculo-cedula_propietario", dividirCedula(inf.cedula_propietario)[1])
                inputsValor("id_form_inv_vehiculo-descripcion", inf.descripcion)
                inputsValor("id_form_inv_vehiculo-material_utilizado", inf.material_utilizado)
                inputsValor("id_form_inv_vehiculo-status", inf.status)

            } else if (inf.tipo_siniestro=="Comercio") {
                inputsValor("id_form_inv_comercio-nombre_comercio", inf.nombre_comercio_investigacion)
                inputsValor("id_form_inv_comercio-rif_comercio", inf.rif_comercio_investigacion)
                inputsValor("id_form_inv_comercio-nombre_propietario", inf.nombre_propietario_comercio)
                inputsValor("id_form_inv_comercio-apellido_propietario", inf.apellido_propietario_comercio)
                inputsValor("id_form_inv_comercio-nacionalidad", dividirCedula(inf.cedula_propietario_comercio)[0])
                inputsValor("id_form_inv_comercio-cedula_propietario", dividirCedula(inf.cedula_propietario_comercio)[1])
                inputsValor("id_form_inv_comercio-descripcion", inf.descripcion_comercio)
                inputsValor("id_form_inv_comercio-material_utilizado", inf.material_utilizado_comercio)
                inputsValor("id_form_inv_comercio-status", inf.status_comercio)

            }

            break;

        case 20:
            inputsValor("id_reinspeccion_prevencion-nombre_comercio", inf.nombre_comercio)
            inputsValor("id_reinspeccion_prevencion-rif_comercio", inf.rif_comercio)
            inputsValor("id_reinspeccion_prevencion-nombre", inf.nombre)
            inputsValor("id_reinspeccion_prevencion-apellidos", inf.apellido)
            inputsValor("id_reinspeccion_prevencion-nacionalidad", dividirCedula(inf.cedula)[0])
            inputsValor("id_reinspeccion_prevencion-cedula", dividirCedula(inf.cedula)[1])
            inputsValor("id_reinspeccion_prevencion-sexo", inf.sexo)
            inputsValor("id_reinspeccion_prevencion-telefono", inf.telefono)
            inputsValor("id_reinspeccion_prevencion-descripcion", inf.descripcion)
            inputsValor("id_reinspeccion_prevencion-material_utilizado", inf.material_utilizado)
            inputsValor("id_reinspeccion_prevencion-status", inf.status)

            break;

        case 21:
            if (inf.tipo_cilindro === "Oxigeno") {
                inf.tipo_cilindro = 2
            } else if (inf.tipo_cilindro === "GLP"){
                inf.tipo_cilindro = 1
            } else {
                inf.tipo_cilindro = 3
            }

            inputsValor("id_retencion_preventiva-tipo_cilindro", inf.tipo_cilindro)
            inputsValor("id_retencion_preventiva-capacidad", inf.capacidad)
            inputsValor("id_retencion_preventiva-serial", inf.serial)
            inputsValor("id_retencion_preventiva-nro_constancia_retencion", inf.nro_constancia)
            inputsValor("id_retencion_preventiva-nombre", inf.nombre)
            inputsValor("id_retencion_preventiva-apellidos", inf.apellidos)
            inputsValor("id_retencion_preventiva-nacionalidad", dividirCedula(inf.cedula)[0])
            inputsValor("id_retencion_preventiva-cedula", dividirCedula(inf.cedula)[1])
            inputsValor("id_retencion_preventiva-descripcion", inf.descripcion)
            inputsValor("id_retencion_preventiva-material_utilizado", inf.material_utilizado)
            inputsValor("id_retencion_preventiva-status", inf.status)
            break;


        
        case 45:

            if (inf.dependencia === "Capacitacion") {
                inputsValor("id_form_capacitacion-tipo_capacitacion", inf.tipo_capacitacion)
                inputsValor("id_form_capacitacion-tipo_clasificacion", inf.tipo_clasificacion)
                inputsValor("id_form_capacitacion-personas_beneficiadas", inf.personas_beneficiadas)
                inputsValor("id_form_capacitacion-descripcion", inf.descripcion)
                inputsValor("id_form_capacitacion-material_utilizado", inf.material_utilizado)
                inputsValor("id_form_capacitacion-status", inf.status)
            } else if (inf.dependencia === "Frente Preventivo") {
                inputsValor("id_form_frente_preventivo-nombre_actividad", inf.nombre_actividad)
                inputsValor("id_form_frente_preventivo-estrategia", inf.estrategia)
                inputsValor("id_form_frente_preventivo-personas_beneficiadas", inf.personas_beneficiadas)
                inputsValor("id_form_frente_preventivo-descripcion", inf.descripcion)
                inputsValor("id_form_frente_preventivo-material_utilizado", inf.material_utilizado)
                inputsValor("id_form_frente_preventivo-status", inf.status)
            } else if (inf.dependencia === "Brigada Juvenil") {
                let tipo_capacitacion = ""
                if (inf.tipo_capacitacion != "Charla" || inf.tipo_capacitacion != "Taller" || inf.tipo_capacitacion != "Curso") {
                    tipo_capacitacion = "Otros"
                    inputsValor("id_form_brigada-otros", inf.tipo_capacitacion)
                }
                inputsValor("id_form_brigada-tipo_capacitacion", tipo_capacitacion  )
                inputsValor("id_form_brigada-tipo_clasificacion", inf.tipo_clasificacion)
                inputsValor("id_form_brigada-personas_beneficiadas", inf.personas_beneficiadas)
                inputsValor("id_form_brigada-descripcion", inf.descripcion)
                inputsValor("id_form_brigada-material_utilizado", inf.material_utilizado)
                inputsValor("id_form_brigada-status", inf.status)
            }
            break;

        default:
            break;
    }
}

function dividirCedula(cedula) {
    let [l, n] = cedula.split("-");
    
    return [l, n]
}

function inputsValor(id, valor) {
    document.getElementById(id).value = valor
}
function atributeDisable(id) {
    document.getElementById(id).style = "pointer-events: none; background-color: #e9ecef;"
}


// window.addEventListener('beforeunload', () => {
//     // Eliminar la clave del localStorage
//     localStorage.removeItem('fetchedData');
// });

// window.addEventListener('popstate', () => {
//     // Eliminar la clave del localStorage al retroceder
//     localStorage.removeItem('fetchedData');
// });

})