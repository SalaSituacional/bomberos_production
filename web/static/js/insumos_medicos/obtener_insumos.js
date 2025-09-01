// La función `$(document).ready()` se asegura de que el código
// se ejecute solo cuando el DOM (la estructura de la página)
// esté completamente cargado y seguro de manipular.
$(document).ready(function() {

    // Cacheamos los elementos del DOM que vamos a usar.
    // Esto hace el código más eficiente y legible.
    const $form = $('form[data-url]');
    const $insumoSelect = $('#id_insumo');
    const $loteSelect = $('#id_lote');
    
    // Obtenemos la URL y el ID del inventario directamente del atributo 'data-url' del formulario.
    const ajaxUrl = $form.data('url');
    const inventarioId = $form.data('inventario-id');

    // Deshabilitamos el select de Lote al cargar la página.
    // Se habilitará solo cuando se seleccione un insumo.
    $loteSelect.prop('disabled', true);

    // Evento que se dispara cada vez que el valor del select de Insumo cambia.
    $insumoSelect.change(function() {
        // Obtenemos el ID del insumo seleccionado.
        const insumoId = $(this).val();

        // Si se selecciona un insumo válido (no la opción vacía)
        if (insumoId) {
            // Realizamos la petición AJAX para obtener los lotes.
            $.ajax({
                url: ajaxUrl,
                data: {
                    'insumo_id': insumoId,
                    'inventario_id': inventarioId
                },
                dataType: 'json',
                success: function(data) {
                    // Limpiamos y rellenamos el select de Lote.
                    $loteSelect.html('<option value="">---------</option>');
                    if (data.lotes && data.lotes.length > 0) {
                        $.each(data.lotes, function(index, lote) {
                            $loteSelect.append(
                                $('<option></option>').val(lote.id).text(lote.text)
                            );
                        });
                        $loteSelect.prop('disabled', false);
                    } else {
                        // Si no hay lotes, lo deshabilitamos y mostramos un mensaje.
                        $loteSelect.prop('disabled', true);
                        $loteSelect.html('<option value="">No hay lotes disponibles</option>');
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Error en la petición AJAX:", status, error);
                    $loteSelect.html('<option value="">Error al cargar los lotes</option>').prop('disabled', true);
                }
            });
        } else {
            // Si no se selecciona un insumo, reseteamos el select de Lote.
            $loteSelect.html('<option value="">---------</option>').prop('disabled', true);
        }
    });
});
