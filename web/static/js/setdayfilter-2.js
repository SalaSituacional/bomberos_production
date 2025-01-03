document.addEventListener("DOMContentLoaded", function () {
  // Función para obtener la fecha actual en formato "YYYY-MM-DD" ajustada a la zona horaria de Venezuela (UTC-4)
  function getVenezuelanDate() {
    const now = new Date();

    // Crear un objeto de fecha ajustado para UTC-4 (Venezuela)
    const venezuelanDate = new Date(
      now.getUTCFullYear(),
      now.getUTCMonth(),
      now.getUTCDate(),
      now.getUTCHours() - 4, // Ajustar las horas a UTC-4
      now.getUTCMinutes(),
      now.getUTCSeconds()
    );

    // Formatear la fecha a "YYYY-MM-DD"
    const year = venezuelanDate.getFullYear();
    const month = String(venezuelanDate.getMonth() + 1).padStart(2, '0'); // Mes comienza en 0
    const day = String(venezuelanDate.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // Obtener la fecha actual en formato "YYYY-MM-DD" en la zona horaria de Venezuela
  const formattedToday = getVenezuelanDate();

  // Seleccionar todas las filas de la tabla
  const rows = document.querySelectorAll("#data-table tbody tr");

  // Iterar sobre cada fila
  rows.forEach((row) => {
    // Obtener la fecha de la fila (suponiendo que esté en la octava celda)
    const dateCell = row.cells[6]; // Índice 8 corresponde a la columna de Fecha
    const rowDate = dateCell.textContent.trim(); // Formato DD-MM-YYYY

    // Convertir la fecha de la fila al formato "YYYY-MM-DD"
    const [day, month, year] = rowDate.split("-");
    const formattedRowDate = `${year}-${month}-${day}`; // "YYYY-MM-DD"

    // Comparar la fecha de la fila con la fecha actual
    if (formattedRowDate !== formattedToday) {
      row.style.display = "none"; // Oculta la fila si no coincide
    }
  });
});
