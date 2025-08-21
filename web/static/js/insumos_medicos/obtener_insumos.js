// En tu archivo obtener_insumos.js
$(document).ready(function() {
    
    // Obtenemos los valores de los atributos de datos del formulario
    const form = $('form');
    const ObtenerInsumosAjaxUrl = form.data('url');
    const inventarioId = form.data('inventario-id');

    var insumo_id = $('#id_insumo').val();
    if (insumo_id) {
        cargarLotes(insumo_id);
    }

    $('#id_insumo').change(function() {
        var insumo_id = $(this).val();
        cargarLotes(insumo_id);
    });

    /**
     * Realiza una llamada AJAX para cargar los lotes de un insumo específico.
     * @param {string} insumo_id - El ID del insumo seleccionado.
     */
    function cargarLotes(insumo_id) {
        if (!insumo_id || inventarioId === null || inventarioId === 0) {
            console.error("IDs de insumo o inventario no encontrados. No se puede realizar la petición AJAX.");
            var lote_select = $('#id_lote');
            lote_select.empty().append($('<option></option>').val('').text('Primero selecciona un insumo.'));
            return;
        }

        var url = `${ObtenerInsumosAjaxUrl}?insumo_id=${insumo_id}&inventario_id=${inventarioId}`;

        console.log("URL de AJAX:", url); // Log de la URL para depuración

        $.ajax({
            url: url,
            success: function(response) {
                var lote_select = $('#id_lote');
                lote_select.empty();
                
                if (response.lotes && response.lotes.length > 0) {
                    lote_select.append($('<option></option>').val('').text('Seleccione un lote...'));
                    $.each(response.lotes, function(index, lote) {
                        lote_select.append($('<option></option>').val(lote.id).text(lote.text));
                    });
                } else {
                    lote_select.append($('<option></option>').val('').text('No hay lotes disponibles.'));
                }
            },
            error: function(xhr, status, error) {
                console.error("Error en la petición AJAX:", error);
                var lote_select = $('#id_lote');
                lote_select.empty().append($('<option></option>').val('').text('Error al cargar los lotes.'));
            }
        });
    }
});