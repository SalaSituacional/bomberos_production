function ocultarCheckbox(id) {
    const checkbox = document.getElementById(id);
    checkbox.checked = false; // Desmarcar el checkbox
  }
  
  function ocultElement(element) {
    document.getElementById(`${element}`).style.display = "none";
    document
      .getElementById(`${element}`)
      .querySelectorAll("input, select")
      .forEach((ele) => {
        ele.removeAttribute("required");
      });
      document.getElementById(element).querySelectorAll("input[type='checkbox']").checked = false;
  }
  
  function mostrarElement(element) {
    document.getElementById(`${element}`).style.display = "flex";
    document
      .getElementById(`${element}`)
      .querySelectorAll("input, select")
      .forEach((ele) => {
        ele.setAttribute("required", "true");
      });
  }
  
  function mostrarElementNoRequired(element) {
    document.getElementById(`${element}`).style.display = "flex";
    document
      .getElementById(`${element}`)
      .querySelectorAll("input:not([type='checkbox']), select")
      .forEach((ele) => {
        ele.setAttribute("required", "true");
      });
  }
  
  function mostrarElementBlock(element) {
    document.getElementById(`${element}`).style.display = "block";
    document
      .getElementById(`${element}`)
      .querySelectorAll("input, select")
      .forEach((ele) => {
        ele.setAttribute("required", "true");
      });
  }
  
  function mostrarElementBlockNoRequired(element) {
    document.getElementById(`${element}`).style.display = "block";
  }
  
  document
    .getElementById("id_form1-opciones")
    .addEventListener("change", function () {
      switch (this.value) {
        case "1":
          // rescate
          ocultElement("capacitacion")
          ocultElement("form_enfermeria");
          mostrarElement("form_general");
          ocultElement("servicios_medicos");
          ocultElement("psicologia")
          mostrarElement("tipos_procedimientos_title")
          mostrarElement("tipos_procedimientos")
          document.getElementById("id_form2-unidad").parentElement.style.display = "flex"
          document.getElementById("id_form2-unidad").setAttribute("required", true)
          requiredFalse()
          
          mostrarElementBlockNoRequired("form_comisionoes")
  
          document.getElementById("id_form_comision-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_uno")
            } else {
              ocultElement("comision_uno")
              ocultarCheckbox("id_datos_comision_uno-agregar")
              ocultElement("comision_tres")
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
            }
          })
          
          document.getElementById("id_datos_comision_uno-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_dos")
            } else {
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
              ocultElement("comision_tres")
            }
          })
          document.getElementById("id_datos_comision_dos-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_tres")
            } else {
              ocultElement("comision_tres")
            }
          })
  
          break;
        case "2":
          // operaciones
          ocultElement("capacitacion")
          ocultElement("form_enfermeria");
          mostrarElement("form_general");
          ocultElement("servicios_medicos");
          ocultElement("psicologia")
          mostrarElement("tipos_procedimientos_title")
          mostrarElement("tipos_procedimientos")
          requiredFalse()
          document.getElementById("id_form2-unidad").parentElement.style.display = "flex"
          document.getElementById("id_form2-unidad").setAttribute("required", true)
  
          
          mostrarElementBlockNoRequired("form_comisionoes")
  
          document.getElementById("id_form_comision-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_uno")
            } else {
              ocultElement("comision_uno")
              ocultarCheckbox("id_datos_comision_uno-agregar")
              ocultElement("comision_tres")
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
            }
          })
          
          document.getElementById("id_datos_comision_uno-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_dos")
            } else {
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
              ocultElement("comision_tres")
            }
          })
          document.getElementById("id_datos_comision_dos-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_tres")
            } else {
              ocultElement("comision_tres")
            }
          })
          break;
        case "3":
          // Prevencion
          ocultElement("capacitacion")
          ocultElement("form_enfermeria");
          mostrarElement("form_general");
          ocultElement("servicios_medicos");
          ocultElement("psicologia")
          mostrarElement("tipos_procedimientos_title")
          mostrarElement("tipos_procedimientos")
          // document.getElementById("id_form2-unidad").parentElement.style.display = "none"
          // document.getElementById("id_form2-unidad").removeAttribute("required")
          requiredFalse()
  
          
          mostrarElementBlockNoRequired("form_comisionoes")
  
          document.getElementById("id_form_comision-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_uno")
            } else {
              ocultElement("comision_uno")
              ocultarCheckbox("id_datos_comision_uno-agregar")
              ocultElement("comision_tres")
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
            }
          })
          
          document.getElementById("id_datos_comision_uno-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_dos")
            } else {
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
              ocultElement("comision_tres")
            }
          })
          document.getElementById("id_datos_comision_dos-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_tres")
            } else {
              ocultElement("comision_tres")
            }
          })
          break;
        case "4":
          // Grumae
          ocultElement("capacitacion")
          ocultElement("form_enfermeria");
          mostrarElement("form_general");
          ocultElement("servicios_medicos");
          ocultElement("psicologia")
          mostrarElement("tipos_procedimientos_title")
          mostrarElement("tipos_procedimientos")
          document.getElementById("id_form2-unidad").parentElement.style.display = "flex"
          document.getElementById("id_form2-unidad").setAttribute("required", true)
          requiredFalse()
  
          
          mostrarElementBlockNoRequired("form_comisionoes")
  
          document.getElementById("id_form_comision-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_uno")
            } else {
              ocultElement("comision_uno")
              ocultarCheckbox("id_datos_comision_uno-agregar")
              ocultElement("comision_tres")
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
            }
          })
          
          document.getElementById("id_datos_comision_uno-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_dos")
            } else {
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
              ocultElement("comision_tres")
            }
          })
          document.getElementById("id_datos_comision_dos-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_tres")
            } else {
              ocultElement("comision_tres")
            }
          })
          break;
        case "5":
          // prehospitalaria
          ocultElement("capacitacion")
          ocultElement("form_enfermeria");
          ocultElement("servicios_medicos");
          ocultElement("psicologia")
          mostrarElement("form_general");
          mostrarElement("tipos_procedimientos_title")
          mostrarElement("tipos_procedimientos")
          document.getElementById("id_form2-unidad").parentElement.style.display = "flex"
          document.getElementById("id_form2-unidad").setAttribute("required", true)
          requiredFalse()
  
          
          mostrarElementBlockNoRequired("form_comisionoes")
  
          document.getElementById("id_form_comision-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_uno")
            } else {
              ocultElement("comision_uno")
              ocultarCheckbox("id_datos_comision_uno-agregar")
              ocultElement("comision_tres")
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
            }
          })
          
          document.getElementById("id_datos_comision_uno-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_dos")
            } else {
              ocultarCheckbox("id_datos_comision_dos-agregar")
              ocultElement("comision_dos")
              ocultElement("comision_tres")
            }
          })
          document.getElementById("id_datos_comision_dos-agregar").addEventListener("change", function () {
            if (this.checked == true) {
              mostrarElementNoRequired("comision_tres")
            } else {
              ocultElement("comision_tres")
            }
          })
          break;
        case "6":
          // enfermeria
          ocultElement("capacitacion")
          ocultElement("form_general");
          ocultElement("servicios_medicos");
          mostrarElement("form_enfermeria");
          ocultElement("psicologia")
          mostrarElement("tipos_procedimientos")
          mostrarElement("tipos_procedimientos_title")
          document.getElementById("id_form4-tipo_procedimiento").parentElement.querySelector("label").textContent = "Tipo de Atencion"
  
          document.getElementById("id_form_enfermeria-especifique").parentElement.style.display = "none"
          document.getElementById("id_form_enfermeria-especifique").removeAttribute("required")
  
          ocultElement("form_comisionoes")
  
          document.getElementById("id_form_enfermeria-encargado_area").addEventListener("change", function () {
            if (this.value === "Otro"){
              document.getElementById("id_form_enfermeria-especifique").parentElement.style.display = "block"
              document.getElementById("id_form_enfermeria-especifique").setAttribute("required", true)
            } else{
              document.getElementById("id_form_enfermeria-especifique").parentElement.style.display = "none"
              document.getElementById("id_form_enfermeria-especifique").removeAttribute("required")
            }
          })
  
          requiredFalse()
          break;
        case "7":
          // servicios Medicos
          ocultElement("form_general");
          ocultElement("form_enfermeria");
          mostrarElement("servicios_medicos")
          ocultElement("capacitacion")
          ocultElement("psicologia")
          mostrarElement("tipos_procedimientos")
          mostrarElement("tipos_procedimientos_title")
          ocultElement("form_comisionoes")
          requiredFalse()
          break;
        case "8":
          // psicologia
          ocultElement("form_general");
          ocultElement("form_enfermeria");
          ocultElement("servicios_medicos")
          ocultElement("capacitacion")
          mostrarElement("psicologia")
          mostrarElement("tipos_procedimientos")
          mostrarElement("tipos_procedimientos_title")
          ocultElement("form_comisionoes")
          requiredFalse()
          break;
        case "9":
          // capacitacion
          ocultElement("form_general");
          ocultElement("form_enfermeria");
          ocultElement("servicios_medicos")
          ocultElement("psicologia")
          ocultElement("tipos_procedimientos")
          ocultElement("tipos_procedimientos_title")
          mostrarElement("capacitacion")
          ocultElement("form_comisionoes")
          requiredFalse()
          let input_solicitante = document.getElementById("id_form_capacitacion-solicitante")
          let seleccion = document.getElementById("id_form_capacitacion-dependencia")
          
          document.getElementById("id_form_capacitacion-solicitante_externo").parentElement.style.display = "none"
          document.getElementById("id_form_capacitacion-solicitante_externo").removeAttribute("required")
  
          input_solicitante.addEventListener("change", function () {
            if (this.value === "0"){
              document.getElementById("id_form_capacitacion-solicitante_externo").parentElement.style.display = "flex"
              document.getElementById("id_form_capacitacion-solicitante_externo").setAttribute("required", "true")
            } else{
              document.getElementById("id_form_capacitacion-solicitante_externo").parentElement.style.display = "none"
              document.getElementById("id_form_capacitacion-solicitante_externo").removeAttribute("required")
            }
          })
  
          seleccion.addEventListener("change", function () {
            if (this.value === "Capacitacion") {
              mostrarElementBlock("detalles_capacitacion")
              ocultElement("detalles_frente_preventivo")
              ocultElement("detalles_brigada")
              document.getElementById("button_submit").style.display = "block";
              
            } else if (this.value === "Brigada Juvenil") {
              mostrarElementBlock("detalles_brigada")
              ocultElement("detalles_capacitacion")
              ocultElement("detalles_frente_preventivo")
              document.getElementById("button_submit").style.display = "block";
  
              // document.getElementById("id_form_brigada-tipo_capacitacion").parentElement.style.display = "none"
              document.getElementById("id_form_brigada-otros").parentElement.style.display = "none"
              document.getElementById("id_form_brigada-otros").removeAttribute("required")
  
              document.getElementById("id_form_brigada-tipo_capacitacion").addEventListener("change", function (){
                if (this.value == "Otros"){
                  document.getElementById("id_form_brigada-otros").parentElement.style.display = "block"
                  document.getElementById("id_form_brigada-otros").setAttribute("required", true)
                } else {
                  document.getElementById("id_form_brigada-otros").parentElement.style.display = "none"
                  document.getElementById("id_form_brigada-otros").removeAttribute("required")
                }
              })
  
  
            } else {
              mostrarElementBlock("detalles_frente_preventivo")
              ocultElement("detalles_capacitacion")
              ocultElement("detalles_brigada")
              document.getElementById("button_submit").style.display = "block";
            }
          })
  
          break;
      }
    });