// < !--Script para cambiar el menu desplegable de tipo de procedimiento segun la division-- >
function hideAllForms() {
  const forms = document.querySelectorAll(".disp-none");
  forms.forEach((form) => {
    form.style.display = "none";
  });
}

function requiredFalse() {
  const campos = document
    .getElementById("detalles-form")
    .querySelectorAll("select, input");
  campos.forEach((campo) => {
    campo.removeAttribute("required");
  });
}

function requiredExceptions(elements) {
  const campos = elements;
  campos.forEach((campo) => {
    campo.removeAttribute("required");
  });
}


// <!--Script para el manejo de formularios-- >
document
  .getElementById("id_form4-tipo_procedimiento")
  .addEventListener("change", function () {
    const elementsToHide = [
      "abast_agua",
      "apoyo_unid",
      "guard_prev",
      "atend_no_efect",
      "desp_seguridad",
      "falsa_alarm",
      "serv_especiales",
      "fallecidos",
      "rescate",
      "rescate_animal",
      "rescate_persona",
      "incendio_form",
      "retencion_preventiva_incendio",
      "persona_presente",
      "detalles_vehiculo",
      "atenciones_paramedicas",
      "emergencias_medicas",
      "traslados_emergencias",
      "accidentes_transito",
      "vehiculo_accidente",
      "otro_vehiculo_accidente",
      "otro_vehiculo_accidente2",
      "lesionado_accidente",
      "lesionado_accidente2",
      "lesionado_accidente3",
      "traslado_accidente",
      "traslado_accidente2",
      "traslado_accidente3",
      "evaluacion_riesgo",
      "mitigacion_riesgo",
      "puesto_avanzada",
      "traslados_prehospitalaria",
      "asesoramiento_form",
      "form_persona_presente",
      "reinspeccion_prevencion",
      "retencion_preventiva",
      "artificios_pirotecnico",
      "lesionados",
      "incendio_art",
      "fallecidos_art",
      "detalles_vehiculo_art",
      "persona_presente_art",
      "inspeccion_art_pir",
      "valoracion_medica",
      "detalles_enfermeria",
      "detalles_psicologia",
      "detalles_capacitacion",
      "detalles_frente_preventivo",
      "jornada_medica",
      "form_inpecciones",
      "form_inspecciones_prevencion",
      "form_inspecciones_habitabilidad",
      "form_inspecciones_arbol",
      "form_inspecciones_otros",
      "form_investigacion",
      "form_inv_vehiculo",
      "form_inv_comercio",
      "form_inv_estructura",
    ];

    const showElements = (elementsToShow) => {
      // Primero ocultamos todos los elementos, usando la clase 'non-visible'
      elementsToHide.forEach((id) => {
        const element = document.getElementById(id);
        if (element) {
          element.style.display = "none";
        }
      });

      // Luego mostramos los elementos específicos, usando la clase 'visible'
      elementsToShow.forEach((id) => {
        const element = document.getElementById(id);
        if (element) {
          element.style.display = "block";
        }
      });
    };

    let campos;
    switch (this.value) {
      case "1":
        requiredFalse();
        showElements(["abast_agua"]);
        campos = document
          .getElementById("abast_agua")
          .querySelectorAll("select, input");
        setRequired(campos, true); // Agregar required a la nueva sección
        document.getElementById("button_submit").style.display = "block";
        break;
      case "2":
        requiredFalse();
        showElements(["apoyo_unid"]);
        campos = document
          .getElementById("apoyo_unid")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "3":
        requiredFalse();
        showElements(["guard_prev"]);
        campos = document
          .getElementById("guard_prev")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "4":
        requiredFalse();
        showElements(["atend_no_efect"]);
        campos = document
          .getElementById("atend_no_efect")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "5":
        requiredFalse();
        showElements(["desp_seguridad"]);
        campos = document
          .getElementById("desp_seguridad")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "6":
        requiredFalse();
        showElements(["falsa_alarm"]);
        campos = document
          .getElementById("falsa_alarm")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "7":
        requiredFalse();
        showElements(["atenciones_paramedicas"]);
        document.getElementById("button_submit").style.display = "none";

        // Obtener los campos de "atenciones_paramedicas"
        campos = document
          .getElementById("atenciones_paramedicas")
          .querySelectorAll("select, input");
        setRequired(campos, true); // Establecer required en true para los campos de la sección actual

        document
          .getElementById("id_atenciones_paramedicas-tipo_atencion")
          .addEventListener("change", function () {
            // Remover required de los campos de "atenciones_paramedicas" cuando se cambie la opción
            // setRequired(campos, false);

            if (this.value === "Emergencias Medicas") {
              requiredFalse();
              showElements(["atenciones_paramedicas", "emergencias_medicas"]);
              document.getElementById("button_submit").style.display = "block";

              // Obtener los campos de "emergencias_medicas" y establecer required
              let emergenciaCampos = document
                .getElementById("emergencias_medicas")
                .querySelectorAll("select, input");
              let accidentesTransito = document
                .getElementById("accidentes_transito")
                .querySelectorAll("select, input");
              let emergenciaCampos_no = document
                .getElementById("emergencias_medicas")
                .querySelectorAll("input[type='checkbox']");

              setRequired(emergenciaCampos, true);
              requiredExceptions(emergenciaCampos_no);
              requiredExceptions(accidentesTransito);

              document
                .getElementById("traslados_emergencias")
                .querySelectorAll("select, input")
                .forEach((ele) => {
                  ele.removeAttribute("required");
                });

              document
                .getElementById("id_emergencias_medicas-trasladado")
                .addEventListener("change", function () {
                  if (this.checked) {
                    document.getElementById(
                      "traslados_emergencias"
                    ).style.display = "block";
                    document
                      .getElementById("traslados_emergencias")
                      .querySelectorAll("select, input")
                      .forEach((ele) => {
                        ele.setAttribute("required", true);
                      });
                  } else {
                    document.getElementById(
                      "traslados_emergencias"
                    ).style.display = "none";
                    document
                      .getElementById("traslados_emergencias")
                      .querySelectorAll("select, input")
                      .forEach((ele) => {
                        ele.removeAttribute("required");
                      });
                  }
                });
            } else if (this.value === "Accidentes de Transito") {
              requiredFalse();
              showElements(["atenciones_paramedicas", "accidentes_transito"]);
              document.getElementById("button_submit").style.display = "block";

              // Obtener los campos de "accidentes_transito" y establecer required
              let accidenteCampos = document
                .getElementById("accidentes_transito")
                .querySelectorAll("select, input");
              let emergenciaCampos = document
                .getElementById("emergencias_medicas")
                .querySelectorAll("select, input");
              let accidenteCampos_no = document
                .getElementById("accidentes_transito")
                .querySelectorAll("input[type='checkbox']");

              setRequired(accidenteCampos, true);
              requiredExceptions(accidenteCampos_no);
              requiredExceptions(emergenciaCampos);

              requiredExceptions(
                document
                  .getElementById("vehiculo_accidente")
                  .querySelectorAll("select, input")
              );
              requiredExceptions(
                document
                  .getElementById("otro_vehiculo_accidente")
                  .querySelectorAll("select, input")
              );
              requiredExceptions(
                document
                  .getElementById("lesionado_accidente")
                  .querySelectorAll("select, input")
              );
              requiredExceptions(
                document
                  .getElementById("lesionado_accidente2")
                  .querySelectorAll("select, input")
              );
              requiredExceptions(
                document
                  .getElementById("lesionado_accidente3")
                  .querySelectorAll("select, input")
              );
              requiredExceptions(
                document
                  .getElementById("traslado_accidente")
                  .querySelectorAll("select, input")
              );
              requiredExceptions(
                document
                  .getElementById("traslado_accidente2")
                  .querySelectorAll("select, input")
              );
              requiredExceptions(
                document
                  .getElementById("traslado_accidente3")
                  .querySelectorAll("select, input")
              );
              requiredExceptions(
                document
                  .getElementById("otro_vehiculo_accidente2")
                  .querySelectorAll("select, input")
              );

              document
                .getElementById(
                  "id_formulario_accidentes_transito-agg_vehiculo"
                )
                .addEventListener("change", function () {
                  if (this.checked) {
                    document.getElementById(
                      "vehiculo_accidente"
                    ).style.display = "flex";

                    document
                      .getElementById("vehiculo_accidente")
                      .querySelectorAll("select, input")
                      .forEach((ele) => {
                        ele.setAttribute("required", true);
                      });

                    requiredExceptions(
                      document
                        .getElementById("accidentes_transito")
                        .querySelectorAll("input[type='checkbox']")
                    );
                  } else {
                    document.getElementById(
                      "vehiculo_accidente"
                    ).style.display = "none";
                    document
                      .getElementById("vehiculo_accidente")
                      .querySelectorAll("select, input")
                      .forEach((ele) => {
                        ele.removeAttribute("required");
                      });
                  }

                  document
                    .getElementById(
                      "id_detalles_vehiculos_accidentes-agg_vehiculo"
                    )
                    .addEventListener("change", function () {
                      if (this.checked) {
                        document
                          .getElementById("otro_vehiculo_accidente")
                          .querySelectorAll("select, input")
                          .forEach((ele) => {
                            ele.setAttribute("required", true);
                          });
                        document.getElementById(
                          "otro_vehiculo_accidente"
                        ).style.display = "flex";
                        requiredExceptions(
                          document
                            .getElementById("accidentes_transito")
                            .querySelectorAll("input[type='checkbox']")
                        );
                      } else {
                        document
                          .getElementById("otro_vehiculo_accidente")
                          .querySelectorAll("select, input")
                          .forEach((ele) => {
                            ele.removeAttribute("required");
                          });
                        document.getElementById(
                          "otro_vehiculo_accidente"
                        ).style.display = "none";
                      }
                    });
                  document
                    .getElementById(
                      "id_detalles_vehiculos_accidentes2-agg_vehiculo"
                    )
                    .addEventListener("change", function () {
                      if (this.checked) {
                        document
                          .getElementById("otro_vehiculo_accidente2")
                          .querySelectorAll("select, input")
                          .forEach((ele) => {
                            ele.setAttribute("required", true);
                          });
                        document.getElementById(
                          "otro_vehiculo_accidente2"
                        ).style.display = "flex";
                        requiredExceptions(
                          document
                            .getElementById("accidentes_transito")
                            .querySelectorAll("input[type='checkbox']")
                        );
                      } else {
                        document
                          .getElementById("otro_vehiculo_accidente2")
                          .querySelectorAll("select, input")
                          .forEach((ele) => {
                            ele.removeAttribute("required");
                          });
                        document.getElementById(
                          "otro_vehiculo_accidente2"
                        ).style.display = "none";
                      }
                    });
                });

              document
                .getElementById(
                  "id_formulario_accidentes_transito-agg_lesionado"
                )
                .addEventListener("change", function () {
                  if (this.checked) {
                    document
                      .getElementById("lesionado_accidente")
                      .querySelectorAll("select, input")
                      .forEach((ele) => {
                        ele.setAttribute("required", true);
                      });
                    document.getElementById(
                      "lesionado_accidente"
                    ).style.display = "flex";

                    requiredExceptions(
                      document
                        .getElementById("accidentes_transito")
                        .querySelectorAll("input[type='checkbox']")
                    );

                    document
                      .getElementById(
                        "id_detalles_lesionados_accidentes-otro_lesionado"
                      )
                      .addEventListener("change", function () {
                        if (this.checked) {
                          document
                            .getElementById("lesionado_accidente2")
                            .querySelectorAll("select, input")
                            .forEach((ele) => {
                              ele.setAttribute("required", true);
                            });
                          document.getElementById(
                            "lesionado_accidente2"
                          ).style.display = "flex";

                          requiredExceptions(
                            document
                              .getElementById("accidentes_transito")
                              .querySelectorAll("input[type='checkbox']")
                          );

                          document
                            .getElementById(
                              "id_detalles_lesionados_accidentes2-otro_lesionado"
                            )
                            .addEventListener("change", function () {
                              if (this.checked) {
                                document
                                  .getElementById("lesionado_accidente3")
                                  .querySelectorAll("select, input")
                                  .forEach((ele) => {
                                    ele.setAttribute("required", true);
                                  });
                                document.getElementById(
                                  "lesionado_accidente3"
                                ).style.display = "flex";
                                requiredExceptions(
                                  document
                                    .getElementById("accidentes_transito")
                                    .querySelectorAll("input[type='checkbox']")
                                );
                              } else {
                                document
                                  .getElementById("lesionado_accidente3")
                                  .querySelectorAll("select, input")
                                  .forEach((ele) => {
                                    ele.removeAttribute("required");
                                  });
                                document.getElementById(
                                  "lesionado_accidente3"
                                ).style.display = "none";
                              }
                            });

                          document
                            .getElementById(
                              "id_detalles_lesionados_accidentes3-trasladado"
                            )
                            .addEventListener("change", function () {
                              if (this.checked) {
                                document
                                  .getElementById("traslado_accidente3")
                                  .querySelectorAll("select, input")
                                  .forEach((ele) => {
                                    ele.setAttribute("required", true);
                                  });
                                document.getElementById(
                                  "traslado_accidente3"
                                ).style.display = "flex";
                                requiredExceptions(
                                  document
                                    .getElementById("accidentes_transito")
                                    .querySelectorAll("input[type='checkbox']")
                                );
                              } else {
                                document
                                  .getElementById("traslado_accidente3")
                                  .querySelectorAll("select, input")
                                  .forEach((ele) => {
                                    ele.removeAttribute("required");
                                  });
                                document.getElementById(
                                  "traslado_accidente3"
                                ).style.display = "none";
                              }
                            });
                        } else {
                          document
                            .getElementById("lesionado_accidente2")
                            .querySelectorAll("select, input")
                            .forEach((ele) => {
                              ele.removeAttribute("required");
                            });
                          document.getElementById(
                            "lesionado_accidente2"
                          ).style.display = "none";
                        }
                      });

                    document
                      .getElementById(
                        "id_detalles_lesionados_accidentes2-trasladado"
                      )
                      .addEventListener("change", function () {
                        if (this.checked) {
                          document
                            .getElementById("traslado_accidente2")
                            .querySelectorAll("select, input")
                            .forEach((ele) => {
                              ele.setAttribute("required", true);
                            });
                          requiredExceptions(
                            document
                              .getElementById("accidentes_transito")
                              .querySelectorAll("input[type='checkbox']")
                          );
                          document.getElementById(
                            "traslado_accidente2"
                          ).style.display = "flex";
                        } else {
                          document
                            .getElementById("traslado_accidente2")
                            .querySelectorAll("select, input")
                            .forEach((ele) => {
                              ele.removeAttribute("required");
                            });
                          document.getElementById(
                            "traslado_accidente2"
                          ).style.display = "none";
                        }
                      });
                  } else {
                    document
                      .getElementById("lesionado_accidente")
                      .querySelectorAll("select, input")
                      .forEach((ele) => {
                        ele.removeAttribute("required");
                      });
                    document.getElementById(
                      "lesionado_accidente"
                    ).style.display = "none";
                  }

                  document
                    .getElementById(
                      "id_detalles_lesionados_accidentes-trasladado"
                    )
                    .addEventListener("change", function () {
                      if (this.checked) {
                        document
                          .getElementById("traslado_accidente")
                          .querySelectorAll("select, input")
                          .forEach((ele) => {
                            ele.setAttribute("required", true);
                          });
                        document.getElementById(
                          "traslado_accidente"
                        ).style.display = "flex";
                        requiredExceptions(
                          document
                            .getElementById("accidentes_transito")
                            .querySelectorAll("input[type='checkbox']")
                        );
                      } else {
                        document
                          .getElementById("traslado_accidente")
                          .querySelectorAll("select, input")
                          .forEach((ele) => {
                            ele.removeAttribute("required");
                          });
                        document.getElementById(
                          "traslado_accidente"
                        ).style.display = "none";
                      }
                    });
                });
            }

            // // Al final, establecer required en true para los campos de la sección activa
            // campos = document.getElementById("atenciones_paramedicas").querySelectorAll("select, input");
            // setRequired(campos, true);
          });
        break;
      case "9":
        requiredFalse();
        showElements(["serv_especiales"]);
        campos = document
          .getElementById("serv_especiales")
          .querySelectorAll("select, input");
        setRequired(campos, true); // Agregar required a la nueva sección
        document.getElementById("button_submit").style.display = "block";
        break;
      case "10":
        requiredFalse();
        showElements(["rescate"]);
        campos = document.getElementById("rescate").querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "none";
        document
          .getElementById("id_rescate_form-tipo_rescate")
          .addEventListener("change", function () {
            if (this.value == "1") {
              requiredExceptions(
                document
                  .getElementById("rescate_persona")
                  .querySelectorAll("select, input")
              );
              showElements(["rescate", "rescate_animal"]);
              let campos2 = document
                .getElementById("rescate_animal")
                .querySelectorAll("select, input");
              setRequired(campos2, true);
              document.getElementById("button_submit").style.display = "block";
            } else if (this.value != "1") {
              let rescate_persona = document
                .getElementById("rescate_persona")
                .querySelector("h4");
              let titulo = this.options[this.selectedIndex].text;
              // console.log(rescate_persona, titulo)
              rescate_persona.textContent = titulo;
              requiredExceptions(
                document
                  .getElementById("rescate_animal")
                  .querySelectorAll("select, input")
              );
              showElements(["rescate", "rescate_persona"]);
              let campos2 = document
                .getElementById("rescate_persona")
                .querySelectorAll("select, input");
              setRequired(campos2, true);
              document.getElementById("button_submit").style.display = "block";
            }
          });
        break;
      case "11":
        requiredFalse();
        showElements(["incendio_form"]);
        campos = document
          .getElementById("incendio_form")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        requiredExceptions(
          document
            .getElementById("detalles_vehiculo")
            .querySelectorAll("select, input")
        );
        requiredExceptions(
          document
            .getElementById("persona_presente")
            .querySelectorAll("select, input")
        );
        requiredExceptions(
          document
            .getElementById("retencion_preventiva_incendio")
            .querySelectorAll("select, input")
        );
        requiredExceptions(
          document
            .getElementById("incendio_form")
            .querySelectorAll("input[type='checkbox']")
        );
        document.getElementById("id_incendio_form-check_retencion").parentElement.style.display = "none"

        document
          .getElementById("id_incendio_form-check_agregar_persona")
          .addEventListener("change", function () {
            if (this.checked) {
              let campo2 = document
                .getElementById("persona_presente")
                .querySelectorAll("select, input");
              setRequired(campo2, true);
              document.getElementById("persona_presente").style.display =
                "flex";
            } else {
              let campo2 = document
                .getElementById("persona_presente")
                .querySelectorAll("select, input");
              requiredExceptions(campo2);
              document.getElementById("persona_presente").style.display =
                "none";
            }
          });

        document.getElementById("id_incendio_form-tipo_incendio").addEventListener("change", function (){
          if (this.value == "7") {
            document.getElementById("id_incendio_form-check_retencion").parentElement.style.display = "flex"
          } else {
            document.getElementById("id_incendio_form-check_retencion").parentElement.style.display = "none"
          }
        })


        document
          .getElementById("id_incendio_form-check_retencion")
          .addEventListener("change", function () {
            if (this.checked) {
              let campo2 = document
                .getElementById("retencion_preventiva_incendio")
                .querySelectorAll("select, input");
              setRequired(campo2, true);
              document.getElementById("retencion_preventiva_incendio").style.display =
                "flex";
            } else {
              let campo2 = document
                .getElementById("retencion_preventiva_incendio")
                .querySelectorAll("select, input");
              requiredExceptions(campo2);
              document.getElementById("retencion_preventiva_incendio").style.display =
                "none";
            }
          });



        document
          .getElementById("id_incendio_form-tipo_incendio")
          .addEventListener("change", function () {
            if (this.value == "2") {
              let campo2 = document
                .getElementById("detalles_vehiculo")
                .querySelectorAll("select, input");
              setRequired(campo2, true);
              document.getElementById("detalles_vehiculo").style.display =
                "flex";
            } else {
              let campo2 = document
                .getElementById("detalles_vehiculo")
                .querySelectorAll("select, input");
              requiredExceptions(campo2);
              document.getElementById("detalles_vehiculo").style.display =
                "none";
            }
          });
        document.getElementById("button_submit").style.display = "block";
        break;
      case "12":
        requiredFalse();
        showElements(["fallecidos"]);
        campos = document
          .getElementById("fallecidos")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "13":
        requiredFalse();
        showElements(["mitigacion_riesgo"]);
        
        campos = document
        .getElementById("mitigacion_riesgo")
        .querySelectorAll("select, input");
        setRequired(campos, true);
        
        requiredExceptions(
          document
            .getElementById("mitigacion_riesgo")
            .querySelectorAll("input[type='checkbox']")
        );
        document.getElementById("id_mitigacion_riesgo_form-agregar_vehiculo").parentElement.style.display = "none"
        
        document.getElementById("button_submit").style.display = "block";
        
        
        document.getElementById("id_mitigacion_riesgo_form-tipo_riesgo").addEventListener("change", function () {
          if (this.value === "1") {
            document.getElementById("id_mitigacion_riesgo_form-agregar_vehiculo").parentElement.style.display = "flex"
          } else {
            document.getElementById("id_mitigacion_riesgo_form-agregar_vehiculo").parentElement.style.display = "none"            
          }
        })

        document.getElementById("id_mitigacion_riesgo_form-agregar_vehiculo").addEventListener("change", function () {
          if (this.checked) {
            let campo2 = document
                .getElementById("vehiculo_derrame_form")
                .querySelectorAll("select, input");
              setRequired(campo2, true);
              document.getElementById("vehiculo_derrame_form").style.display =
                "block";
          } else {
            let campo2 = document
                .getElementById("vehiculo_derrame_form")
                .querySelectorAll("select, input");
              requiredExceptions(campo2);
              document.getElementById("vehiculo_derrame_form").style.display =
                "none";
          }
        })

        document.getElementById("id_vehiculo_derrame_form-agregar_segundo_vehiculo").addEventListener("change", function () {
          if (this.checked) {
            let campo2 = document
                .getElementById("vehiculo_derrame_form2")
                .querySelectorAll("select, input");
              setRequired(campo2, true);
              document.getElementById("vehiculo_derrame_form2").style.display =
                "block";
          } else {
            let campo2 = document
                .getElementById("vehiculo_derrame_form2")
                .querySelectorAll("select, input");
              requiredExceptions(campo2);
              document.getElementById("vehiculo_derrame_form2").style.display =
                "none";
          }
        })

        document.getElementById("id_vehiculo_derrame_form2-agregar_tercer_vehiculo").addEventListener("change", function () {
          if (this.checked) {
            let campo2 = document
                .getElementById("vehiculo_derrame_form3")
                .querySelectorAll("select, input");
              setRequired(campo2, true);
              document.getElementById("vehiculo_derrame_form3").style.display =
                "block";
          } else {
            let campo2 = document
                .getElementById("vehiculo_derrame_form3")
                .querySelectorAll("select, input");
              requiredExceptions(campo2);
              document.getElementById("vehiculo_derrame_form3").style.display =
                "none";
          }
        })



        break;
      case "14":
        let select_vivienda = document
          .getElementById("evaluacion_riesgo");
        select_vivienda.style.display = "none";
        requiredFalse();
        showElements(["evaluacion_riesgo"]);
        campos = document
          .getElementById("evaluacion_riesgo")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        let campos2 = document
          .getElementById("form_persona_presente")
          .querySelectorAll("select, input");

        document
          .getElementById("id_evaluacion_riesgo_form-tipo_riesgo")
          .addEventListener("change", function () {
            if (this.value === "1") {
              select_vivienda.style.display = "flex";
              select_vivienda.querySelector("select").value = ""; // Borra la selección
              let campos3 = select_vivienda.querySelectorAll("select, input");
              setRequired(campos3, "true");
            } else {
              select_vivienda.style.display = "none";
              select_vivienda.querySelector("select").value = ""; // Borra la selección
              requiredExceptions(
                select_vivienda.querySelectorAll("select, input")
              );
            }
          });

        query = document.getElementById("id_form1-opciones");
        if (query.value === "3") {
          showElements(["evaluacion_riesgo"]);
          setRequired(campos2, true);
          document.getElementById("form_persona_presente").style.display =
            "flex";
        } else {
          requiredExceptions(campos2);
        }
        break;
      case "15":
        requiredFalse();
        showElements(["puesto_avanzada"]);
        campos = document
          .getElementById("puesto_avanzada")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "16":
        requiredFalse();
        showElements(["traslados_prehospitalaria"]);
        campos = document
          .getElementById("traslados_prehospitalaria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "17":
        requiredFalse();
        showElements(["asesoramiento_form"]);
        campos = document
          .getElementById("asesoramiento_form")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "18":
        requiredFalse();
        showElements(["form_inpecciones"]);
        campos = document
          .getElementById("form_inpecciones")
          .querySelectorAll("select, input");
        setRequired(campos, true);

        document.getElementById("id_form_inspecciones-tipo_inspeccion").addEventListener("change", function () {
          switch (this.value){
            case "Prevención":
              ocultElement("form_inspecciones_arbol")
              ocultElement("form_inspecciones_habitabilidad")
              ocultElement("form_inspecciones_otros")
              mostrarElementBlock("form_inspecciones_prevencion")
              document.getElementById("form_inspecciones_prevencion").querySelector("h4").textContent = "Inspeccion de Prevencion"
              document.getElementById("button_submit").style.display = "block";
              break;

            case "Árbol":
              ocultElement("form_inspecciones_prevencion")
              ocultElement("form_inspecciones_habitabilidad")
              ocultElement("form_inspecciones_otros")
              mostrarElementBlock("form_inspecciones_arbol")
              document.getElementById("form_inspecciones_arbol").querySelector("h4").textContent = "Inspeccion de Árbol"
              document.getElementById("button_submit").style.display = "block";
              break;

            case "Asesorias Tecnicas":
              ocultElement("form_inspecciones_arbol")
              ocultElement("form_inspecciones_habitabilidad")
              ocultElement("form_inspecciones_otros")
              mostrarElementBlock("form_inspecciones_prevencion")
              document.getElementById("form_inspecciones_prevencion").querySelector("h4").textContent = "Asesorias Tecnicas"
              document.getElementById("button_submit").style.display = "block";
              break;

            case "Habitabilidad":
              ocultElement("form_inspecciones_arbol")
              ocultElement("form_inspecciones_prevencion")
              ocultElement("form_inspecciones_otros")
              mostrarElementBlock("form_inspecciones_habitabilidad")
              document.getElementById("form_inspecciones_habitabilidad").querySelector("h4").textContent = "Inspeccion de Habitabilidad"
              document.getElementById("button_submit").style.display = "block";
              break;

            case "Otros":
              ocultElement("form_inspecciones_arbol")
              ocultElement("form_inspecciones_prevencion")
              ocultElement("form_inspecciones_habitabilidad")
              mostrarElementBlock("form_inspecciones_otros")
              document.getElementById("form_inspecciones_otros").querySelector("h4").textContent = "Inspecciones (Otros)"
              document.getElementById("button_submit").style.display = "block";
              break;

          }
        })
        
        break;
      case "19":
        requiredFalse();
        showElements(["form_investigacion"]);
        campos = document
          .getElementById("form_investigacion")
          .querySelectorAll("select, input");
        setRequired(campos, true);

        document.getElementById("id_form_investigacion-tipo_siniestro").addEventListener("change", function () {
          switch (this.value){
            case "Comercio":
              ocultElement("form_inv_vehiculo")
              ocultElement("form_inv_estructura")
              mostrarElementBlock("form_inv_comercio")
              document.getElementById("form_inv_comercio").querySelector("h4").textContent = "Investigacion Comercio"
              document.getElementById("button_submit").style.display = "block";
              break;

            case "Estructura":
              ocultElement("form_inv_vehiculo")
              ocultElement("form_inv_comercio")
              mostrarElementBlock("form_inv_estructura")
              document.getElementById("form_inv_estructura").querySelector("h4").textContent = "Investigacion de Estructura"
              document.getElementById("button_submit").style.display = "block";
              break;

            case "Vehiculo":
              ocultElement("form_inv_estructura")
              ocultElement("form_inv_comercio")
              mostrarElementBlock("form_inv_vehiculo")
              document.getElementById("form_inv_vehiculo").querySelector("h4").textContent = "Investigacion Vehiculo"
              document.getElementById("button_submit").style.display = "block";
              break;

            case "Vivienda":
              ocultElement("form_inv_vehiculo")
              ocultElement("form_inv_comercio")
              mostrarElementBlock("form_inv_estructura")
              document.getElementById("form_inv_estructura").querySelector("h4").textContent = "Investigacion de Vivienda"
              document.getElementById("button_submit").style.display = "block";
              break;
          }
        })
        
        break;
      case "20":
        requiredFalse();
        showElements(["reinspeccion_prevencion"]);
        campos = document
          .getElementById("reinspeccion_prevencion")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "21":
        requiredFalse();
        showElements(["retencion_preventiva"]);
        campos = document
          .getElementById("retencion_preventiva")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "22":
        requiredFalse();
        showElements(["artificios_pirotecnico"]);
        campos = document
          .getElementById("artificios_pirotecnico")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        requiredExceptions(
          document
            .getElementById("detalles_vehiculo_art")
            .querySelectorAll("select, input")
        );
        requiredExceptions(
          document
            .getElementById("persona_presente_art")
            .querySelectorAll("select, input")
        );
        document
          .getElementById("id_artificios_pirotecnico-tipo_procedimiento")
          .addEventListener("change", function () {
            switch (this.value) {
              case "1":
                showElements(["artificios_pirotecnico", "incendio_art"]);
                campos = document
                  .getElementById("incendio_art")
                  .querySelectorAll("select, input");
                setRequired(campos, true);
                requiredExceptions(
                  document
                    .getElementById("detalles_vehiculo_art")
                    .querySelectorAll("select, input")
                );
                requiredExceptions(
                  document
                    .getElementById("persona_presente_art")
                    .querySelectorAll("select, input")
                );
                requiredExceptions(
                  document
                    .getElementById("incendio_art")
                    .querySelectorAll("input[type='checkbox']")
                );

                requiredExceptions(
                  document
                    .getElementById("lesionados")
                    .querySelectorAll("select, input")
                );
                requiredExceptions(
                  document
                    .getElementById("fallecidos_art")
                    .querySelectorAll("select, input")
                );

                document
                  .getElementById("id_incendio_art-check_agregar_persona")
                  .addEventListener("change", function () {
                    if (this.checked) {
                      let campo2 = document
                        .getElementById("persona_presente_art")
                        .querySelectorAll("select, input");
                      setRequired(campo2, true);
                      document.getElementById(
                        "persona_presente_art"
                      ).style.display = "flex";
                    } else {
                      let campo2 = document
                        .getElementById("persona_presente_art")
                        .querySelectorAll("select, input");
                      requiredExceptions(campo2);
                      document.getElementById(
                        "persona_presente_art"
                      ).style.display = "none";
                    }
                  });
                document
                  .getElementById("id_incendio_art-tipo_incendio")
                  .addEventListener("change", function () {
                    if (this.value == "2") {
                      let campo2 = document
                        .getElementById("detalles_vehiculo_art")
                        .querySelectorAll("select, input");
                      setRequired(campo2, true);
                      document.getElementById(
                        "detalles_vehiculo_art"
                      ).style.display = "flex";
                    } else {
                      let campo2 = document
                        .getElementById("detalles_vehiculo_art")
                        .querySelectorAll("select, input");
                      requiredExceptions(campo2);
                      document.getElementById(
                        "detalles_vehiculo_art"
                      ).style.display = "none";
                    }
                  });
                document.getElementById("button_submit").style.display =
                  "block";
                break;
              case "2":
                showElements(["artificios_pirotecnico", "lesionados"]);
                campos = document
                  .getElementById("lesionados")
                  .querySelectorAll("select, input");
                setRequired(campos, true);
                requiredExceptions(
                  document
                    .getElementById("fallecidos_art")
                    .querySelectorAll("select, input")
                );
                requiredExceptions(
                  document
                    .getElementById("incendio_art")
                    .querySelectorAll("select, input")
                );
                document.getElementById("button_submit").style.display =
                  "block";
                break;
              case "3":
                showElements(["artificios_pirotecnico", "fallecidos_art"]);
                campos = document
                  .getElementById("fallecidos_art")
                  .querySelectorAll("select, input");
                setRequired(campos, true);
                requiredExceptions(
                  document
                    .getElementById("lesionados")
                    .querySelectorAll("select, input")
                );
                requiredExceptions(
                  document
                    .getElementById("incendio_art")
                    .querySelectorAll("select, input")
                );
                document.getElementById("button_submit").style.display =
                  "block";
                break;
            }
          });

        break;
      case "23":
        requiredFalse();
        showElements(["inspeccion_art_pir"]);
        campos = document
          .getElementById("inspeccion_art_pir")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        // requiredExceptions(document.getElementById("detalles_vehiculo_art").querySelectorAll("select, input"))
        // requiredExceptions(document.getElementById("persona_presente_art").querySelectorAll("select, input"))
        break;
      case "24":
        requiredFalse();
        showElements(["valoracion_medica"]);
        campos = document
          .getElementById("valoracion_medica")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "25":
        requiredFalse();
        showElements(["jornada_medica"]);
        campos = document
          .getElementById("jornada_medica")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("button_submit").style.display = "block";
        break;
      case "26":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Administración de Medicamentos"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "27":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
         document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Administración de Tratamientos"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "28":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Aerosolterapia"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "29":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Atención Local"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "30":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Atención Prehospitalaria"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "31":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Cuantificación de Presión Arterial"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "32":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Cuantificación de Signos Vitales"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "33":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Cura"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "34":
        requiredFalse();
        showElements(["detalles_enfermeria"]);
        campos = document
          .getElementById("detalles_enfermeria")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_enfermeria").querySelector("h4").textContent = "Otro"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "35":
        requiredFalse();
        showElements(["detalles_psicologia"]);
        campos = document
          .getElementById("detalles_psicologia")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_psicologia").querySelector("h4").textContent = "Certificado de Salud Mental"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "36":
        requiredFalse();
        showElements(["detalles_psicologia"]);
        campos = document
          .getElementById("detalles_psicologia")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_psicologia").querySelector("h4").textContent = "Consulta Bombero Activo"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "37":
        requiredFalse();
        showElements(["detalles_psicologia"]);
        campos = document
          .getElementById("detalles_psicologia")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_psicologia").querySelector("h4").textContent = "Consulta Integrante Brigada Juvenil"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "38":
        requiredFalse();
        showElements(["detalles_psicologia"]);
        campos = document
          .getElementById("detalles_psicologia")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_psicologia").querySelector("h4").textContent = "Consulta Paciente Externo"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "39":
        requiredFalse();
        showElements(["detalles_psicologia"]);
        campos = document
          .getElementById("detalles_psicologia")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_psicologia").querySelector("h4").textContent = "Evaluacion Psicologica Postvacacional"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "40":
        requiredFalse();
        showElements(["detalles_psicologia"]);
        campos = document
          .getElementById("detalles_psicologia")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_psicologia").querySelector("h4").textContent = "Evaluacion Psicologica Prevacacional"
        document.getElementById("button_submit").style.display = "block";
        break;
      case "41":
        requiredFalse();
        showElements(["detalles_psicologia"]);
        campos = document
          .getElementById("detalles_psicologia")
          .querySelectorAll("select, input");
        setRequired(campos, true);
        document.getElementById("detalles_psicologia").querySelector("h4").textContent = "Evaluacion Personal Nuevo Ingreso"
        document.getElementById("button_submit").style.display = "block";
        break;
      default:
        elementsToHide.forEach((id) => {
          document.getElementById(id).style.display = "none";
          campos = document
            .getElementById(id)
            .querySelectorAll("select, input");
          setRequired(campos, false); // Remover required de los campos ocultos
        });
        break;
    }

    // Función para establecer el atributo required
    function setRequired(campos, isRequired) {
      campos.forEach((campo) => {
        if (isRequired) {
          campo.setAttribute("required", true);
        } else {
          campo.removeAttribute("required");
        }
      });
    }
  });

