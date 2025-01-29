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
  "#F25C54",   // Rojo coral
  "#1A6FB9",  // Azul fuerte
  "#FFCC5C",  // Amarillo cálido
  "#B0BEC5",  // Gris suave
  "#FF9A00",  // Naranja brillante
  "#4ECDC4",  // Verde aqua
  "#2E8BC0",  // Azul claro
  "#FF6B6B",  // Rojo vibrante
  "#5ABF80"  // Verde menta
];


// Graficas de tortas ===================================================================================================================================================

// ACTUALIZADAS ===========================================================

// Función genérica para crear o actualizar gráficos
function createOrUpdateChart(ctx, chart, type, labels, data) {
  if (chart) chart.destroy(); // Destruir gráfico previo si existe

  if (type === "polarArea"){
    return new Chart(ctx, {
      type: type,
      data: {
        labels: labels,
        datasets: [
          {
            label: "Procedimientos",
            data: data,
            borderWidth: 2,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        scales: {
          r: {
            min: 0,
            ticks: {
              beginAtZero: true,
              stepSize: 2,
              callback: function (data) {
                return Math.round(data);
              },
            },
          },
        },
      },
      plugins: [ChartDataLabels], // Habilitar el plugin
    });
  } 
  else{
    return new Chart(ctx, {
      type: type,
      data: {
        labels: labels,
        datasets: [
          {
            label: "Procedimientos",
            data: data,
            borderWidth: 2,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        plugins: {
          legend: {
            display: true,
            labels: {
              font: {
                size: 24,
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

  // Inicializar gráficos según la configuración
  chartConfigs.forEach((config) => {
    const { selectElement, monthPicker, ctxId, endpoint, type, labelField, valueField, defaultOption } = config;
    const chartRef = { chart: null };

    // Establecer valor por defecto
    selectElement.value = selectElement.options[defaultOption].value;

    selectElement.addEventListener("change", () =>
      updateChart(endpoint, ctxId, selectElement, monthPicker, chartRef, type, labelField, valueField)
    );

    monthPicker.addEventListener("change", () =>
      updateChart(endpoint, ctxId, selectElement, monthPicker, chartRef, type, labelField, valueField)
    );

    // Cargar gráfica inicial
    updateChart(endpoint, ctxId, selectElement, monthPicker, chartRef, type, labelField, valueField);
  });
});


// Grafica de Barras =======================================================================================================================================================

document.addEventListener("DOMContentLoaded", function () {
  let chart; // Declarar chart fuera de las funciones para que sea accesible
  const ctx6 = document.getElementById("bar").getContext("2d");

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
    return Object.entries(data).map(([division, detalles]) => ({
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

    const fontSize = window.innerWidth < 376 ? 10 : 15; // Tamaño dinámico de fuente

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
        plugins: {
          legend: { display: false },
        },
        scales: {
          x: { ticks: { font: { size: fontSize } } },
          y: { ticks: { font: { size: fontSize + 3 } } }, // Incremento para el eje Y
        },
      },
      formatter: (value, context) => {
        // Personalización de los números
        const dataset = context.chart.data.datasets[0];
        const total = dataset.data.reduce((sum, num) => sum + num, 0);

        // Personalización: Formato como porcentaje
        const percentage = ((value / total) * 100).toFixed(2);

        // Personalización: Texto adicional
        return `$${value} \n(${percentage}%)`; // Retorna el valor en dólares y porcentaje
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

