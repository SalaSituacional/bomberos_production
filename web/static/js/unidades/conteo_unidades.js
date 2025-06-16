fetchWithLoader("/mecanica/api/conteo_unidades/")
  .then(response => response)
  .then(data => conteoUnidades(data))
  .catch(error => console.error("Error al obtener los datos", error));

function conteoUnidades(data) {
    document.getElementById("Mantenimiento").innerHTML = data.en_mantenimiento
    document.getElementById("Disponibles").innerHTML = data.activa
    document.getElementById("FueraServicio").innerHTML = data.fuera_de_servicio
}