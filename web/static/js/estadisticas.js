// Listado de Procedimientos ====================================================================================================
document.getElementById("monthSelector").addEventListener("change", function () {
  const selectedMonth = this.value; // Captura el valor del selector de mes
  obtenerResultados(selectedMonth);
});

function obtenerResultados(selectedMonth) {
  const url = selectedMonth
    ? `/api/generar_estadistica/?month=${selectedMonth}`
    : `/api/generar_estadistica/`; // Solicitud sin el parámetro `month` para obtener todo el año

  fetchWithLoader(url)
    .then((data) => {
      // Elementos de lista para cada división
      const listaOperaciones = document.getElementById("list_operaciones");
      const listaPrehospitalaria = document.getElementById(
        "list_prehospitalaria"
      );
      const listaMedicos = document.getElementById("list_medicos");
      const listaGrumae = document.getElementById("list_grumae");
      const listaRescate = document.getElementById("list_rescate");
      const listaPrevencion = document.getElementById("list_prevencion");
      const listaEnfermeria = document.getElementById("list_enfermeria");
      const listaCapacitacion = document.getElementById("list_capacitacion");
      const listaPsicologia = document.getElementById("list_psicologia");

      // Limpiar las listas antes de agregar nuevos datos
      listaOperaciones.innerHTML = "";
      listaPrehospitalaria.innerHTML = "";
      listaMedicos.innerHTML = "";
      listaGrumae.innerHTML = "";
      listaRescate.innerHTML = "";
      listaPrevencion.innerHTML = "";
      listaEnfermeria.innerHTML = "";
      listaCapacitacion.innerHTML = "";
      listaPsicologia.innerHTML = "";

      // Función para procesar y añadir datos a cada lista
      function procesarDivision(dataDivision, listaElemento) {
        if (dataDivision) {
          for (const tipoProcedimiento in dataDivision.detalles) {
            // Crear elemento <li> para el tipo de procedimiento
            const li = document.createElement("li");
            li.textContent = `${tipoProcedimiento}: ${dataDivision.total_por_tipo[tipoProcedimiento]}`;

            // Crear lista interna de parroquias y cantidades
            const ulParroquias = document.createElement("ol");

            // Añadir cada parroquia y su cantidad a la lista interna
            for (const parroquia in dataDivision.detalles[tipoProcedimiento]) {
              const cantidad =
                dataDivision.detalles[tipoProcedimiento][parroquia];
              const liParroquia = document.createElement("li");
              liParroquia.textContent = `${parroquia}: ${cantidad}`;
              ulParroquias.appendChild(liParroquia);
            }

            // Añadir lista de parroquias al elemento <li> del tipo de procedimiento
            li.appendChild(ulParroquias);

            // Añadir el <li> del tipo de procedimiento a la lista principal
            listaElemento.appendChild(li);
          }
        }
      }

      // Llamar a la función para cada división con sus respectivos elementos
      procesarDivision(data.Operaciones, listaOperaciones);
      procesarDivision(data.Prehospitalaria, listaPrehospitalaria);
      procesarDivision(data.ServiciosMédicos, listaMedicos);
      procesarDivision(data.Grumae, listaGrumae);
      procesarDivision(data.Rescate, listaRescate);
      procesarDivision(data.Prevención, listaPrevencion);
      procesarDivision(data.Enfermería, listaEnfermeria);
      procesarDivision(data.Capacitación, listaCapacitacion);
      procesarDivision(data.Psicología, listaPsicologia);
    })
    .catch((error) => {
      console.error("Error al obtener datos:", error);
    });
}

// Llamada inicial para cargar los datos de todo el año al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  obtenerResultados(""); // Llama a `obtenerResultados` sin ningún mes seleccionado para obtener datos del año
});

const colors = [
  "#F25C54", // Rojo coral
  "#1A6FB9", // Azul fuerte
  "#FFCC5C", // Amarillo cálido
  "#B0BEC5", // Gris suave
  "#FF9A00", // Naranja brillante
  "#4ECDC4", // Verde aqua
  "#2E8BC0", // Azul claro
  "#FF6B6B", // Rojo vibrante
  "#5ABF80", // Verde menta
];

// Graficas de tortas ===================================================================================================================================================

// ACTUALIZADAS ===========================================================

// Función genérica para crear o actualizar gráficos
function createOrUpdateChart(ctx, chart, type, labels, data) {
  if (chart) chart.destroy(); // Destruir gráfico previo si existe

  const canvasElement = ctx.canvas;
  // Eliminar atributos width y height del HTML para que Chart.js y CSS tomen el control
  canvasElement.removeAttribute('width');
  canvasElement.removeAttribute('height');
  
  // Definir tamaños de fuente dinámicos basados en el ancho de la ventana
  const isMobile = window.innerWidth <= 650;
  const datalabelsFontSize = isMobile ? 14 : 18.5; // Reducido para móvil
  const legendFontSize = isMobile ? 12 : 18; // Reducido para móvil
  const ticksFontSize = isMobile ? 10 : 13; // Reducido para móvil

  // Obtener el ancho del contenedor padre para calcular el ancho del canvas
  // Asegúrate de que el parentElement exista antes de acceder a clientWidth
  const parentWidth = canvasElement.parentElement ? canvasElement.parentElement.clientWidth : window.innerWidth;
  const desiredHeight = isMobile ? 250 : 360; // Altura fija para móvil, altura un poco mayor para escritorio

  // Establecer las dimensiones de renderizado del canvas y sus estilos de visualización
  canvasElement.width = parentWidth;
  canvasElement.height = desiredHeight;
  canvasElement.style.width = `${parentWidth}px`;
  canvasElement.style.height = `${desiredHeight}px`;

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false, // Permite que el canvas se ajuste libremente
    plugins: {
      datalabels: {
        color: 'white',
        font: {
          size: datalabelsFontSize,
        },
        formatter: (value, context) => {
          // Formateo para mostrar el valor y porcentaje en gráficos de pastel/donas
          const dataset = context.chart.data.datasets[0];
          const total = dataset.data.reduce((sum, num) => sum + num, 0);
          return `${value}`;
        },
      },
    },
    // Ajustes de diseño para evitar que se vea colapsado
    layout: {
      padding: {
        left: isMobile ? 10 : 20,
        right: isMobile ? 10 : 20,
        top: isMobile ? 10 : 20,
        bottom: isMobile ? 10 : 20,
      }
    }
  };

  if (type === "polarArea") {
    return new Chart(ctx, {
      type: type,
      data: {
        labels: labels,
        datasets: [
          {
            label: "Procedimientos",
            data: data,
            borderWidth: 1,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        ...commonOptions, // Incluir opciones comunes
        scales: {
          r: {
            min: 0,
            ticks: {
              beginAtZero: true,
              stepSize: 2,
              callback: function (data) {
                return Math.round(data);
              },
              font: {
                size: ticksFontSize, // Aplicar tamaño de fuente dinámico
              }
            },
            pointLabels: { // Etiquetas de los puntos en el área polar
                font: {
                    size: ticksFontSize, // Aplicar tamaño de fuente dinámico
                }
            }
          },
        },
        plugins: {
            ...commonOptions.plugins, // Mantener datalabels
            legend: {
                display: true,
                labels: {
                    font: {
                        size: legendFontSize, // Aplicar tamaño de fuente dinámico
                    },
                },
            },
        },
      },
      plugins: [ChartDataLabels], // Habilitar el plugin
    });
  } else { // Para tipos 'pie' y 'doughnut'
    return new Chart(ctx, {
      type: type,
      data: {
        labels: labels,
        datasets: [
          {
            label: "Procedimientos",
            data: data,
            borderWidth: 1,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        ...commonOptions, // Incluir opciones comunes
        plugins: {
          ...commonOptions.plugins, // Mantener datalabels
          legend: {
            display: true,
            position: isMobile ? 'bottom' : 'right', // Posición de la leyenda más adecuada para móvil
            labels: {
              font: {
                size: legendFontSize, // Aplicar tamaño de fuente dinámico
              },
            },
          },
        },
      },
      plugins: [ChartDataLabels], // Habilitar el plugin
    });
  }
}

// Función genérica para manejar la lógica de cada gráfico
async function updateChart(
  endpoint,
  ctxId,
  selectElement,
  monthPicker,
  chartRef,
  type,
  labelField,
  valueField
) {
  const selectedValue = selectElement.value;
  const selectedMonth = monthPicker.value;

  const data = await fetchWithLoader(`${endpoint}?param_id=${selectedValue}&mes=${selectedMonth}`);
  const ctx = document.getElementById(ctxId).getContext("2d");

  if (!data || data.length === 0) {
    // Crear gráfico vacío si no hay datos
    chartRef.chart = createOrUpdateChart(ctx, chartRef.chart, type, ["Ninguno"], [0]);
    return;
  }

  const labels = data.map((item) => item[labelField]);
  const values = data.map((item) => item[valueField]);

  // Actualizar o crear gráfico
  chartRef.chart = createOrUpdateChart(ctx, chartRef.chart, type, labels, values);
}

// Configuración de gráficos
document.addEventListener("DOMContentLoaded", function () {
  const chartConfigs = [
    {
      selectElement: document.querySelector(".form-select-sm"),
      monthPicker: document.getElementById("month-picker2"),
      ctxId: "pie",
      endpoint: "/api/procedimientos_division/",
      type: "pie",
      labelField: "id_tipo_procedimiento__tipo_procedimiento",
      valueField: "count",
      defaultOption: 6,
    },
    {
      selectElement: document.querySelector(".form-select-sm2"),
      monthPicker: document.getElementById("month-picker3"),
      ctxId: "pie_two",
      endpoint: "/api/procedimientos_division/",
      type: "pie",
      labelField: "id_tipo_procedimiento__tipo_procedimiento",
      valueField: "count",
      defaultOption: 4,
    },
    {
      selectElement: document.querySelector(".form-select-sm3"),
      monthPicker: document.getElementById("month-picker4"),
      ctxId: "donuts",
      endpoint: "/api/procedimientos_division_parroquia/",
      type: "doughnut",
      labelField: "id_parroquia__parroquia",
      valueField: "count",
      defaultOption: 1,
    },
    {
      selectElement: document.querySelector(".form-select-sm4"),
      monthPicker: document.getElementById("month-picker5"),
      ctxId: "donuts_two",
      endpoint: "/api/procedimientos_division_parroquia/",
      type: "doughnut",
      labelField: "id_parroquia__parroquia",
      valueField: "count",
      defaultOption: 2,
    },
    {
      selectElement: document.querySelector(".form-select-sm5"),
      monthPicker: document.getElementById("month-picker6"),
      ctxId: "polar",
      endpoint: "/api/procedimientos_tipo/",
      type: "polarArea",
      labelField: "id_division__division",
      valueField: "count",
      defaultOption: 9,
    },
    {
      selectElement: document.querySelector(".form-select-sm6"),
      monthPicker: document.getElementById("month-picker7"),
      ctxId: "polar2",
      endpoint: "/api/procedimientos_tipo_parroquias/",
      type: "polarArea",
      labelField: "id_parroquia__parroquia",
      valueField: "count",
      defaultOption: 7,
    },
    {
      selectElement: document.querySelector(".form-select-sm7"),
      monthPicker: document.getElementById("month-picker8"),
      ctxId: "pie3",
      endpoint: "/api/procedimientos_tipo_detalles/",
      type: "polarArea",
      labelField: "tipo_servicio",
      valueField: "count",
      defaultOption: 1,
    },
    {
      selectElement: document.querySelector(".form-select-sm8"),
      monthPicker: document.getElementById("month-picker9"),
      ctxId: "pie4",
      endpoint: "/api/procedimientos_tipo_detalles/",
      type: "polarArea",
      labelField: "tipo_servicio",
      valueField: "count",
      defaultOption: 9,
    },
  ];

  // Referencias para los gráficos de pastel/donas/polar
  const chartRefs = {};

  // Inicializar gráficos según la configuración
  chartConfigs.forEach((config) => {
    const { selectElement, monthPicker, ctxId, endpoint, type, labelField, valueField, defaultOption } = config;
    
    // Almacenar la referencia del gráfico en un objeto para poder destruirlo y recrearlo
    chartRefs[ctxId] = { chart: null };

    // Establecer valor por defecto
    if (selectElement && selectElement.options[defaultOption]) {
      selectElement.value = selectElement.options[defaultOption].value;
    }

    if (selectElement) {
      selectElement.addEventListener("change", () =>
        updateChart(endpoint, ctxId, selectElement, monthPicker, chartRefs[ctxId], type, labelField, valueField)
      );
    }

    if (monthPicker) {
      monthPicker.addEventListener("change", () =>
        updateChart(endpoint, ctxId, selectElement, monthPicker, chartRefs[ctxId], type, labelField, valueField)
      );
    }

    // Cargar gráfica inicial
    updateChart(endpoint, ctxId, selectElement, monthPicker, chartRefs[ctxId], type, labelField, valueField);
  });

  // Escuchar el evento de redimensionamiento de la ventana para todos los gráficos
  window.addEventListener("resize", () => {
    chartConfigs.forEach((config) => {
      const { selectElement, monthPicker, ctxId, endpoint, type, labelField, valueField } = config;
      // Re-renderizar el gráfico con los nuevos tamaños de fuente
      updateChart(endpoint, ctxId, selectElement, monthPicker, chartRefs[ctxId], type, labelField, valueField);
    });
  });
});


// Grafica de Barras =======================================================================================================================================================

document.addEventListener("DOMContentLoaded", function () {
  let chart; // Declarar chart fuera de las funciones para que sea accesible
  const ctx6 = document.getElementById("bar")?.getContext("2d"); // Usar optional chaining por si el elemento no existe

  if (!ctx6) {
    console.warn("Canvas 'bar' no encontrado, omitiendo inicialización del gráfico de barras.");
    return; // Salir si el canvas no existe
  }

  // Función para obtener datos de la API con la función fetchWithLoader
  async function fetchDivisiones(mes = "") {
    try {
      return await fetchWithLoader(`/api/divisiones_estadisticas/?mes=${mes}`);
    } catch (error) {
      console.error("Error fetching divisiones:", error);
      return {};
    }
  }

  // Actualiza las tarjetas con los datos obtenidos
  function updateCards(data) {
    for (const [division, detalles] of Object.entries(data)) {
      const count = detalles.total || 0; // Solo total

      const card = document.querySelector(`li[data-division="${division}"] .count`);
      if (card) {
        card.textContent = count;
      }
    }
  }

  // Extrae divisiones y totales para la gráfica
  function obtenerDivisiones(data) {
    return Object.entries(data).map((
      [division, detalles]) => ({
      division,
      count: detalles.total || 0,
    }));
  }

  // Función para inicializar los datos
  async function init() {
    const data = await fetchDivisiones(); // Sin mes seleccionado
    updateCards(data); // Actualizar las tarjetas con datos totales
    actualizarGrafica(data); // Crear la gráfica
  }

  // Crear o actualizar el gráfico de barras con los datos proporcionados
  function actualizarGrafica(data) {
    const divisiones = obtenerDivisiones(data);
    const labels = divisiones.map((item) => item.division);
    const values = divisiones.map((item) => item.count);

    const canvasElement = ctx6.canvas;
    // Eliminar atributos width y height del HTML para que Chart.js y CSS tomen el control
    canvasElement.removeAttribute('width');
    canvasElement.removeAttribute('height');

    // Definir tamaños de fuente dinámicos basados en el ancho de la ventana
    const isMobile = window.innerWidth <= 376;
    const ticksFontSize = isMobile ? 10 : 15; // Tamaño dinámico de fuente para ejes
    const datalabelsFontSize = isMobile ? 12 : 14; // Reducido para mejor visibilidad fuera de la barra

    // Obtener el ancho del contenedor padre para calcular el ancho del canvas
    const parentWidth = canvasElement.parentElement ? canvasElement.parentElement.clientWidth : window.innerWidth;
    const desiredHeight = isMobile ? 250 : 350; // Altura fija para móvil, altura un poco mayor para escritorio

    // Establecer las dimensiones de renderizado del canvas y sus estilos de visualización
    canvasElement.width = parentWidth;
    canvasElement.height = desiredHeight;
    canvasElement.style.width = `${parentWidth}px`;
    canvasElement.style.height = `${desiredHeight}px`;

    // Destruir el gráfico existente si ya está creado
    if (chart) {
      chart.destroy();
    }

    // Crear un nuevo gráfico de barras
    chart = new Chart(ctx6, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Procedimientos",
            data: values,
            borderWidth: 1,
            backgroundColor: colors, // Colores para las barras
            borderColor: colors, // Colores de bordes
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // Permite que el canvas se ajuste sin forzar tamaño
        plugins: {
          legend: { display: false },
          datalabels: {
            color: 'black', // Cambiado a negro para visibilidad fuera de la barra
            anchor: 'end', // Anclado al final de la barra
            align: 'end', // Alineado al final del ancla (arriba de la barra)
            offset: 4, // Pequeño desplazamiento para separar del borde de la barra
            font: {
              size: datalabelsFontSize, // Aplicar tamaño de fuente dinámico
            },
            formatter: (value, context) => {
              // Personalización de los números
              const dataset = context.chart.data.datasets[0];
              const total = dataset.data.reduce((sum, num) => sum + num, 0);

              // Personalización: Formato como porcentaje
              const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : 0; // Evitar división por cero

              // Personalización: Texto adicional
              return `${value} (${percentage}%)`; // Retorna el valor y porcentaje
            },
          },
        },
        scales: {
          x: {
            ticks: {
              font: {
                size: ticksFontSize, // Aplicar tamaño de fuente dinámico
              },
            },
            grid: {
              display: false // Ocultar líneas de la cuadrícula en el eje X
            }
          },
          y: {
            ticks: {
              font: {
                size: ticksFontSize + 3, // Incremento para el eje Y
              },
            },
            grid: {
              display: false // Ocultar líneas de la cuadrícula en el eje Y
            }
          },
        },
        layout: {
          padding: {
            left: isMobile ? 5 : 20,
            right: isMobile ? 5 : 20,
            top: isMobile ? 20 : 30, // Aumentar padding superior para los labels
            bottom: isMobile ? 10 : 20,
          }
        }
      },
      plugins: [ChartDataLabels], // Habilitar el plugin
    });
  }

  // Ajusta el tamaño de fuente del gráfico según el tamaño de la ventana
  async function updateChartOnResize() {
    const data = await fetchDivisiones(); // Obtener los datos actuales
    actualizarGrafica(data); // Reconstruir el gráfico con el nuevo tamaño de fuente
  }

  // Manejar el evento de cambio del input de mes
  document.getElementById("month-picker").addEventListener("change", async (event) => {
    const mesSeleccionado = event.target.value; // Obtener el valor del mes seleccionado
    const data = await fetchDivisiones(mesSeleccionado); // Llamar a la API con el mes seleccionado
    updateCards(data); // Actualizar las tarjetas
    actualizarGrafica(data); // Actualizar la gráfica
  });

  // Ajustar el tamaño de fuente al cambiar el tamaño de la ventana
  window.addEventListener("resize", updateChartOnResize);

  // Inicializar al cargar la página
  init();
});



// Grafica de Barras Horizontal=======================================================================================================================================================
document.addEventListener("DOMContentLoaded", function () {
  let chart; // Mantener la referencia del gráfico para actualizarlo
  const ctx7 = document.getElementById("bar-horizontal")?.getContext("2d"); // Usar optional chaining por si el elemento no existe

  if (!ctx7) {
    console.warn("Canvas 'bar-horizontal' no encontrado, omitiendo inicialización del gráfico de barras horizontal.");
    return; // Salir si el canvas no existe
  }

  // Definir colores para las barras (si son diferentes a los globales)
  // const colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]; // Usar los colores globales si no hay una razón para cambiarlos

  // Función para obtener datos de la API
  async function fetchDivisionesHorizontal(mes = "") {
    try {
      const response = await fetchWithLoader(`/api/procedimientos_tipo_horizontal/?mes=${mes}`);
      if (!response || !Array.isArray(response)) {
        console.error("Datos no válidos recibidos de la API");
        return [];
      }
      return response;
    } catch (error) {
      console.error("Error obteniendo datos de la API:", error);
      return [];
    }
  }

  // Función para extraer divisiones y totales de la API
  function obtenerDivisiones(data) {
    return data.map(item => ({
      tipo_procedimiento: item.id_tipo_procedimiento__tipo_procedimiento,
      count: item.count || 0,
    }));
  }

  // Función para actualizar las tarjetas de totales
  function updateCards(data) {
    data.forEach(({ tipo_procedimiento, count }) => {
      const card = document.querySelector(`li[data-division="${tipo_procedimiento}"] .count`);
      if (card) {
        card.textContent = count;
      }
    });
  }

  // Función para actualizar o crear la gráfica
  function actualizarGrafica(data) {
    const procedimientos = obtenerDivisiones(data);
    const labels = procedimientos.map(item => item.tipo_procedimiento);
    const values = procedimientos.map(item => item.count);

    const canvasElement = ctx7.canvas;
    // Eliminar atributos width y height del HTML para que Chart.js y CSS tomen el control
    canvasElement.removeAttribute('width');
    canvasElement.removeAttribute('height');

    // Definir tamaños de fuente dinámicos basados en el ancho de la ventana
    const isMobile = window.innerWidth <= 376;
    const ticksFontSize = isMobile ? 12 : 16; // Tamaño dinámico de fuente para etiquetas del eje Y
    const datalabelsFontSize = isMobile ? 12 : 14; // Tamaño dinámico de fuente para datalabels

    // Obtener el ancho del contenedor padre para calcular el ancho del canvas
    const parentWidth = canvasElement.parentElement ? canvasElement.parentElement.clientWidth : window.innerWidth;
    const desiredHeight = isMobile ? (labels.length * 40 + 80) : (labels.length * 30 + 100); // Altura dinámica basada en el número de etiquetas

    // Establecer las dimensiones de renderizado del canvas y sus estilos de visualización
    canvasElement.width = parentWidth;
    canvasElement.height = desiredHeight;
    canvasElement.style.width = `${parentWidth}px`;
    canvasElement.style.height = `${desiredHeight}px`;


    // Destruir el gráfico si ya existe
    if (chart) {
      chart.destroy();
    }

    // Crear la gráfica
    chart = new Chart(ctx7, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Procedimientos",
            data: values,
            borderWidth: 1,
            backgroundColor: colors,
            borderColor: colors,
          },
        ],
      },
      options: {
        indexAxis: 'y', // Eje horizontal
        responsive: true,
        maintainAspectRatio: false, // Permite que el canvas se ajuste sin forzar tamaño
        plugins: {
          legend: { display: false }, // No mostrar leyenda
          datalabels: {
            color: 'black', // Cambiado a negro para visibilidad fuera de la barra
            anchor: 'end', // Anclado al final de la barra
            align: 'end', // Alineado al final del ancla (fuera de la barra)
            offset: 4, // Pequeño desplazamiento para separar del borde de la barra
            font: { size: datalabelsFontSize }, // Tamaño dinámico para datalabels
            formatter: (value, context) => {
              const dataset = context.chart.data.datasets[0];
              const total = dataset.data.reduce((sum, num) => sum + num, 0);
              const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : 0;
              return `${value} (${percentage}%)`;
            },
          },
        },
        layout: {
          padding: {
            left: isMobile ? 5 : 20, // Reducir padding en móvil
            right: isMobile ? 25 : 40, // Aumentar padding a la derecha para los labels
            top: isMobile ? 5 : 20,
            bottom: isMobile ? 5 : 20,
          },
        },
        scales: {
          x: {
            display: false, // Ocultar eje X
            beginAtZero: true, // Asegurar que el eje X comience en cero
            max: Math.max(...values) * 1.2, // Ajustar el máximo del eje X para que los datalabels no se corten
          },
          y: {
            ticks: {
              font: { size: ticksFontSize }, // Tamaño dinámico para etiquetas del eje Y
            },
            grid: {
              display: false // Ocultar líneas de la cuadrícula en el eje Y
            }
          },
        },
      },
      plugins: [ChartDataLabels], // Habilitar el plugin
    });
  }
  // Función para inicializar los datos y la gráfica
  async function init() {
    const data = await fetchDivisionesHorizontal(); // Obtener datos iniciales
    updateCards(data); // Actualizar tarjetas
    actualizarGrafica(data); // Crear gráfica
  }

  // Manejar el cambio del input de mes
  document.getElementById("month-picker-9")?.addEventListener("change", async (event) => { // Optional chaining
    const mesSeleccionado = event.target.value;
    const data = await fetchDivisionesHorizontal(mesSeleccionado);
    updateCards(data);
    actualizarGrafica(data);
  });

  // Manejar el redimensionamiento de la ventana
  window.addEventListener("resize", async () => {
    const data = await fetchDivisionesHorizontal();
    actualizarGrafica(data);
  });

  // Inicializar al cargar la página
  init();
});